#!/usr/bin/env python3 

from pymavlink import mavutil
from math import sqrt
import time
import numpy as np
import threading
import os

os.environ["MAVLINK20"] = "1"


def connect(connection_string):

    vehicle =  mavutil.mavlink_connection(connection_string)

    return vehicle

def VehicleMode(vehicle,mode):

    modes = ["STABILIZE", "ACRO", "ALT_HOLD", "AUTO", "GUIDED", "LOITER", "RTL", "CIRCLE","", "LAND"]
    if mode in modes:
        mode_id = modes.index(mode)
    else:
        mode_id = 12
    ##### changing to guided mode #####
    #mode_id = 0:STABILIZE, 1:ACRO, 2: ALT_HOLD, 3:AUTO, 4:GUIDED, 5:LOITER, 6:RTL, 7:CIRCLE, 9:LAND 12:None
    vehicle.mav.set_mode_send(
        vehicle.target_system,mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,mode_id)

def enable_data_stream(vehicle,stream_rate):

    vehicle.wait_heartbeat()
    vehicle.mav.request_data_stream_send(
    vehicle.target_system, 
    vehicle.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_ALL,
    stream_rate,1)

def arm(vehicle):
    #arm the drone
    vehicle.mav.command_long_send(vehicle.target_system, vehicle.target_component,mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)

def drone_takeoff(vehicle, altitude): 
    # Send MAVLink command to takeoff
    vehicle.mav.command_long_send(
        vehicle.target_system,       # target_system
        vehicle.target_component,    # target_component
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,  # command
        0,                          # confirmation
        0,                          # param1 (min pitch, not used)
        0,                          # param2 (empty for now, not used)
        0,                          # param3 (empty for now, not used)
        0,                          # param4 (yaw angle in degrees, not used)
        0,                          # param5 (latitude, not used)
        0,                          # param6 (longitude, not used)
        altitude                    # param7 (altitude in meters)
    )

def send_velocity_setpoint(vehicle, vx, vy, vz, FRAME):

    # Send MAVLink command to set velocity
    vehicle.mav.set_position_target_local_ned_send(
        0,                          # time_boot_ms (not used)
        vehicle.target_system,       # target_system
        vehicle.target_component,    # target_component
        FRAME,  # frame
        0b0000111111000111,        # type_mask (only vx, vy, vz, yaw_rate)
        0, 0, 0,                    # position (not used)
        vx, vy, vz,                 # velocity in m/s
        0, 0, 0,                    # acceleration (not used)
        0, 0                        # yaw, yaw_rate (not used)
    )

def get_local_position(vehicle):
    while True:
        msg = vehicle.recv_match(type='LOCAL_POSITION_NED', blocking=True)
        if msg is not None:
            pos_x = msg.x # meters
            pos_y = msg.y  # meters
            pos_z = msg.z  # Meters
            vx = msg.vx
            vy = msg.vy
            vz = msg.vz
            return [pos_x,pos_y,pos_z,vx,vy,vz]


def send_velocity_setpoint(vehicle, vx, vy, vz):

    # Send MAVLink command to set velocity
    vehicle.mav.set_position_target_local_ned_send(
        0,                          # time_boot_ms (not used)
        vehicle.target_system,       # target_system
        vehicle.target_component,    # target_component
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,  # frame
        0b0000111111000111,        # type_mask (only vx, vy, vz, yaw_rate)
        0, 0, 0,                    # position (not used)
        vx, vy, vz,                 # velocity in m/s
        0, 0, 0,                    # acceleration (not used)
        0, 0                        # yaw, yaw_rate (not used)
    )
 

def normal_dist_to_wp(vehicle, wp_x, wp_y, wp_z,origin):

    pos = get_local_position(vehicle)
    pos_x = pos[0] + origin[0]
    pos_y = pos[1] + origin[1]
    pos_z = pos[2] + origin[2]

    dist = sqrt((wp_x - pos_x)**2 + (wp_y - pos_y)**2 + (wp_z - pos_z)**2)

    return dist      

def split_mission_points(mission_points, r0_start, r1_start):
    r0_wp = []
    r1_wp = []
    # a spatial clustering + route assignment
    # Assign to nearest drone
    for wp in mission_points:
        d0 = np.linalg.norm(wp[:2] - r0_start[:2])
        d1 = np.linalg.norm(wp[:2] - r1_start[:2])

        if d0 <= d1:
            r0_wp.append(wp)
        else:
            r1_wp.append(wp)

    # Order waypoints for efficient traversal
    def nearest_neighbor_route(start, waypoints):
        if len(waypoints) == 0:
            return []

        remaining = [np.array(wp) for wp in waypoints]
        route = []
        current = np.array(start)

        while remaining:
            distances = [
                np.linalg.norm(wp[:2] - current[:2])
                for wp in remaining
            ]

            idx = np.argmin(distances)

            route.append(remaining.pop(idx))
            current = route[-1]

        return route

    r0_wp = nearest_neighbor_route(r0_start, r0_wp)
    r1_wp = nearest_neighbor_route(r1_start, r1_wp)

    return r0_wp, r1_wp   

def flightMode(vehicle):
    global mode
    vehicle.recv_match(type='HEARTBEAT', blocking=True)
    mode = vehicle.flightmode
    return mode

def arm_status(vehicle):
    heartbeat = vehicle.recv_match(type='HEARTBEAT', blocking=True)
    if heartbeat:
        armed = vehicle.motors_armed()
        if armed==128:
            return True
        else:
            return False

def drone_worker(
        name,
        vehicle,
        task_list,
        other_task_list,controller,origin):

    global r0_alive
    global r1_alive
    counter  = 0
    while True:

        # Check mode
        counter += 1
        mode = flightMode(vehicle)
        print(f"{name} mode: {mode}")
        if mode != "GUIDED":

            print(f"{name} unavailable")

            with lock:

                # Give unfinished jobs away
                while task_list:
                    other_task_list.append(
                        task_list.pop(0)
                    )

            break

        if len(task_list) == 0:

            time.sleep(1)
            continue

        wp = task_list[0]

        x_error = wp[0] - get_local_position(vehicle)[0]+origin[0]
        y_error = wp[1] - get_local_position(vehicle)[1]+origin[1]
        z_error = wp[2] - get_local_position(vehicle)[2]+origin[2]
        # for plotting the trajectory

        vx, vy, vz = controller.update(
            x_error,
            y_error,
            z_error,
            dt
        )

        send_velocity_setpoint(
            vehicle,
            vx,
            vy,
            vz
        )
        print(f"sending velocity setpoint for {name}: vx={vx:.2f}, vy={vy:.2f}, vz={vz:.2f}")
        print(f"current error for {name}: x_error={x_error:.2f}, y_error={y_error:.2f}, z_error={z_error:.2f}")
        dist = np.linalg.norm(
            [x_error, y_error, z_error]
        )

        if dist < 2.0:

            with lock:

                task_list.pop(0)
                wp_reached[tuple(wp)] = True
        time.sleep(0.1)
        print(f"Remaining waypoints for {name}: {len(task_list)}")


class PID:
    def __init__(self, kp, ki, kd,
                 out_limit=None,
                 i_limit=None):

        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.integral = 0.0
        self.prev_error = 0.0

        self.out_limit = out_limit
        self.i_limit = i_limit

    def update(self, error, dt):

        self.integral += error * dt

        if self.i_limit is not None:
            self.integral = max(
                -self.i_limit,
                min(self.integral, self.i_limit)
            )

        derivative = (
            (error - self.prev_error) / dt
            if dt > 0 else 0.0
        )

        output = (
            self.kp * error +
            self.ki * self.integral +
            self.kd * derivative
        )

        if self.out_limit is not None:
            output = max(
                -self.out_limit,
                min(output, self.out_limit)
            )

        self.prev_error = error

        return output

class WaypointController:

    def __init__(self):

        self.pid_x = PID(
            kp=0.5,
            ki=0.0,
            kd=0.2,
            out_limit=3.0
        )

        self.pid_y = PID(
            kp=0.5,
            ki=0.0,
            kd=0.2,
            out_limit=3.0
        )

        self.pid_z = PID(
            kp=1.0,
            ki=0.0,
            kd=0.2,
            out_limit=1.5
        )

    def update(
        self,
        x_error,
        y_error,
        z_error,
        dt
    ):

        vx = self.pid_x.update(x_error, dt)

        vy = self.pid_y.update(y_error, dt)

        vz = self.pid_z.update(z_error, dt)

        return vx, vy, vz
    

mission_points = np.array([
    [0,   -10,  -10],
    [10,  5,  -10],
    [-20, -50,  -12],
    [-35,  20,  -15],
    [80,  50,  -10],
    [20,  10,  -13],
    [60,  15,  -12],
    [35,  8,  -11],
    [-70,  -30,  -16],
    [18,  70,  -15],
])

print("Mission Points (NED):")
print(mission_points)
vehicle_r0 = connect('tcp:127.0.0.1:5763') # aerial robot 0
vehicle_r1 = connect('tcp:127.0.0.1:5773') # aerial robot 1

enable_data_stream(vehicle_r0, stream_rate=100)
enable_data_stream(vehicle_r1, stream_rate=100)

r0_origin = [0,0,0] #initial origin for r0
r1_origin = [0,2,0] #initial origin for r1

r0_waypoints, r1_waypoints = split_mission_points(mission_points, r0_origin, r1_origin)
# print(r0_waypoints, r1_waypoints)
wp_reached = {
    tuple(wp): False
    for wp in mission_points
}
mode = 'GUIDED'
intial_alt = 5
VehicleMode(vehicle_r0, mode)
VehicleMode(vehicle_r1, mode)
arm(vehicle_r0)
arm(vehicle_r1)
time.sleep(4)
drone_takeoff(vehicle_r0, intial_alt)
drone_takeoff(vehicle_r1, intial_alt)
time.sleep(5)  
print("Drones have taken off and are in GUIDED mode.")

controller_r0 = WaypointController()
controller_r1 = WaypointController()

dt = 0.1  #initial time step for PID controller
lock = threading.Lock()  # Create a lock for thread synchronization
r0_status = True
r1_status = True

thread0 = threading.Thread(target=drone_worker, args=("r0", vehicle_r0, r0_waypoints, r1_waypoints, controller_r0,r0_origin))
thread1 = threading.Thread(target=drone_worker, args=("r1", vehicle_r1, r1_waypoints, r0_waypoints, controller_r1,r1_origin))
thread0.start()
thread1.start()

