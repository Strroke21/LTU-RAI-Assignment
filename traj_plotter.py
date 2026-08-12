#!/usr/bin/env python3

import numpy as np
import plotly.graph_objects as go
from pymavlink import mavutil


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

def enable_data_stream(vehicle, stream_rate):

    vehicle.wait_heartbeat()

    vehicle.mav.request_data_stream_send(
        vehicle.target_system,
        vehicle.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL,
        stream_rate,
        1
    )


def connect(connection_string):

    vehicle = mavutil.mavlink_connection(
        connection_string
    )

    return vehicle


def get_local_position(vehicle):

    msg = vehicle.recv_match(
        type='LOCAL_POSITION_NED',
        blocking=True
    )

    if msg is None:
        return None

    return [
        msg.x,
        msg.y,
        msg.z,
        msg.vx,
        msg.vy,
        msg.vz
    ]


def save_plot(
    mission_points,
    r0_x, r0_y, r0_z,
    r1_x, r1_y, r1_z
):

    fig = go.Figure()

    # Mission points (red dots only)
    fig.add_trace(
        go.Scatter3d(
            x=mission_points[:, 0],
            y=mission_points[:, 1],
            z=mission_points[:, 2],
            mode='markers',
            marker=dict(
                size=6,
                color='red'
            ),
            name='Mission Points'
        )
    )

    # r0 trajectory
    if len(r0_x) > 0:

        fig.add_trace(
            go.Scatter3d(
                x=r0_x,
                y=r0_y,
                z=r0_z,
                mode='lines',
                line=dict(
                    color='green',
                    width=6
                ),
                name='r0'
            )
        )

        fig.add_trace(
            go.Scatter3d(
                x=[r0_x[-1]],
                y=[r0_y[-1]],
                z=[r0_z[-1]],
                mode='markers',
                marker=dict(
                    size=8,
                    color='green'
                ),
                name='r0 Current'
            )
        )

    # r1 trajectory
    if len(r1_x) > 0:

        fig.add_trace(
            go.Scatter3d(
                x=r1_x,
                y=r1_y,
                z=r1_z,
                mode='lines',
                line=dict(
                    color='purple',
                    width=6
                ),
                name='r1'
            )
        )

        fig.add_trace(
            go.Scatter3d(
                x=[r1_x[-1]],
                y=[r1_y[-1]],
                z=[r1_z[-1]],
                mode='markers',
                marker=dict(
                    size=8,
                    color='purple'
                ),
                name='r1 Current'
            )
        )

    fig.update_layout(
        title="Multi Robot Simulator",
        scene=dict(
            xaxis_title="North",
            yaxis_title="East",
            zaxis_title="Down"
        ),
        showlegend=True
    )

    fig.write_html(
        "multi_robot_simulator.html"
    )

    print(
        "\nSaved: multi_robot_simulator.html"
    )


def main():

    r0 = connect(
        "tcp:127.0.0.1:5762"
    )

    r1 = connect(
        "tcp:127.0.0.1:5772"
    )

    enable_data_stream(
        r0,
        stream_rate=100
    )

    enable_data_stream(
        r1,
        stream_rate=100
    )

    r0_x, r0_y, r0_z = [], [], []
    r1_x, r1_y, r1_z = [], [], []

    final_wp = mission_points[-1]

    try:

        while True:

            p0 = get_local_position(r0)
            p1 = get_local_position(r1)

            if p0 is not None:

                r0_x.append(p0[0])
                r0_y.append(p0[1])
                r0_z.append(p0[2])

            if p1 is not None:

                r1_x.append(p1[0])
                r1_y.append(p1[1])
                r1_z.append(p1[2])

            print(
                f"r0: {p0[:3] if p0 else None}, "
                f"r1: {p1[:3] if p1 else None}"
            )

            if p0 is not None and p1 is not None:

                dist0 = np.linalg.norm(
                    np.array(p0[:3]) - final_wp
                )

                dist1 = np.linalg.norm(
                    np.array(p1[:3]) - final_wp
                )

                if dist0 < 2.0 and dist1 < 2.0:

                    print("\nMission complete.")

                    save_plot(
                        mission_points,
                        r0_x, r0_y, r0_z,
                        r1_x, r1_y, r1_z
                    )

                    break

    except KeyboardInterrupt:

        print(
            "\nKeyboardInterrupt detected."
        )

        save_plot(
            mission_points,
            r0_x, r0_y, r0_z,
            r1_x, r1_y, r1_z
        )


if __name__ == "__main__":
    main()