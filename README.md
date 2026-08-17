# This repository contains solutions for:
    - Task 2.1: Multi-Robot Exploration and Mission Execution
    - Task 2.2: Semantic Mission Planning using Foundation Models

## Install Dependencies 
```
pip3 install \
    numpy \
    pymavlink \
    ollama

sudo apt install \
    ros-humble-rtabmap-ros \
    ros-humble-cv-bridge \
    ros-humble-image-transport \
    ros-humble-tf2-ros

```

# 1.Multi-Robot Simulator using Ardupilot, ros-humble and gazebo

``` This assumes you have ros2 humble and Ubuntu 22.04 and Gazebo Garden and Arducopter sim_vehicle```
- Multi-UAV simulation in Gazebo Garden
- ArduPilot SITL integration
- RGB-D SLAM using RTAB-Map
- Multi-robot waypoint allocation
- Velocity-based mission execution
- Failure recovery and task reassignment

## Gazebo environment with robots

``` This repo contains robot models and world files used in the simulation. ```

## Clone the Repo and build

```
git clone https://github.com/Strroke21/LTU-RAI-Assignment
cd LTU-RAI-Assignment
colcon build
source ~/LTU-RAI-Assignment/install/setup.bash

```

## Launch Gazebo

```
gz sim -r -v4 LTU_world.sdf 

```

## run gazebo-ros2 sensor bridge
```
ros2 run ltu-sensor-bridge ltu_sensors 

```

## Launch arducopter sim vehicle

``` 
sim_vehicle.py -v copter --model JSON -I0
sim_vehicle.py -v copter --model JSON -I1

```
## Launch RTABMAP for Mapping and Localization for r0 and r1

```
ros2 launch rtabmap_launch rtabmap.launch.py \
namespace:=r0 \
rtabmap_args:="--delete_db_on_start" \
rgb_topic:=/r0/zed2i/image \
depth_topic:=/r0/zed2i/depth_image \
camera_info_topic:=/r0/zed2i/camera_info \
frame_id:=zed2i_camera \
use_sim_time:=true \
approx_sync:=true \
qos:=2 \
rviz:=false \
queue_size:=100

```

```
ros2 launch rtabmap_launch rtabmap.launch.py \
namespace:=r1 \
rtabmap_args:="--delete_db_on_start" \
rgb_topic:=/r1/zed2i/image \
depth_topic:=/r1/zed2i/depth_image \
camera_info_topic:=/r1/zed2i/camera_info \
frame_id:=zed2i_camera \
use_sim_time:=true \
approx_sync:=true \
qos:=2 \
rviz:=false \
queue_size:=100

```
## Run localization node for r0 and r1
```
python3 slam_aero.py #this localises both robots using rgb-d odometry with global fusion

```
## Run Mission Planner 

```
python3 mission_planner.py 
#starts mission and achieves waypoints using velocity control. waypoints are divided into robots using spatial clustering and route assignment. no two robots visit same point at any time. 

```
## Multi-Robot path planning results
- Open the interactive 3D visualization:

### Normal Mission
[Open Interactive 3D Mission Viewer](https://raw.githack.com/Strroke21/LTU-RAI-Assignment/main/multi_robot_simulator.html)

![alt text](https://github.com/Strroke21/LTU-RAI-Assignment/blob/main/mission_plot.png)

### Failure Case
[Open Interactive 3D Mission Viewer](https://raw.githack.com/Strroke21/LTU-RAI-Assignment/main/multi_robot_simulator_Failure_Case.html)

![alt text](https://github.com/Strroke21/LTU-RAI-Assignment/blob/main/failure_result.png)



# 2.Semantic Mission Planning and Agentic Task Decomposition with Foundation Models
- Natural language mission parsing using Llama 3.1 8B
- Semantic scene graph representation
- Language grounding
- Plan validation
- Event-driven replanning

## Download and install Ollama model

```
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b

```
## Install python library for ollama

```
pip3 install ollama

```

## The files required for the tasks are as follows

```
scene_parsing/scene_graph.py #it contains scene description
scene_parsing/grounding.py #grounding is the step that converts LLM words into real objects in the environment.
scene_parsing/planner.py #it contains plan of action
scene_parsing/validator.py #it contains plan validation
scene_parsing/replanner.py #it contains replanning when a plan fails

```
## To execute semantic mission planning run

```
python3 scene_parsing/main.py

```

## Expected Output

```

Mission:
Inspect Building A and then land on the landing pad

Generated Plan
--------------------------------------------------
1. goto -> building_a
2. inspect -> building_a
3. goto -> landing_pad
4. land -> landing_pad

Grounded Plan
--------------------------------------------------
1. goto -> building_a
   type     : building
   position : [20, 10, 0]
2. inspect -> building_a
   type     : building
   position : [20, 10, 0]
3. goto -> landing_pad
   type     : landing_zone
   position : [0, 0, 0]
4. land -> landing_pad
   type     : landing_zone
   position : [0, 0, 0]

Validation
--------------------------------------------------
Validation Passed

Executing Plan
--------------------------------------------------
Executing: goto -> building_a
Executing: inspect -> building_a
Executing: goto -> landing_pad
Executing: land -> landing_pad


========== EVENT ==========
Building A becomes occluded

Replanned Mission

Grounded Plan
--------------------------------------------------
1. goto -> building_b
   type     : building
   position : [60, 20, 0]
2. inspect -> building_b
   type     : building
   position : [60, 20, 0]
3. goto -> landing_pad
   type     : landing_zone
   position : [0, 0, 0]
4. land -> landing_pad
   type     : landing_zone
   position : [0, 0, 0]

Validation
--------------------------------------------------
Validation Passed

Executing Plan
--------------------------------------------------
Executing: goto -> building_b
Executing: inspect -> building_b
Executing: goto -> landing_pad
Executing: land -> landing_pad


========== VALIDATION FAILURE TEST ==========

Generated Plan
--------------------------------------------------
1. goto -> vehicle_1
2. land -> vehicle_1

Grounded Plan
--------------------------------------------------
1. goto -> vehicle_1
   type     : vehicle
   position : [30, -5, 0]
2. land -> vehicle_1
   type     : vehicle
   position : [30, -5, 0]

Validation
--------------------------------------------------

Validation Failed:
Cannot land on vehicle_1. It is a vehicle

========== EVENT ==========
Building B destroyed

New Mission Generated

Grounded Plan
--------------------------------------------------
1. goto -> emergency_zone
   type     : landing_zone
   position : [10, 5, 0]
2. land -> emergency_zone
   type     : landing_zone
   position : [10, 5, 0]

Validation
--------------------------------------------------
Validation Passed

Executing Plan
--------------------------------------------------
Executing: goto -> emergency_zone
Executing: land -> emergency_zone

```
