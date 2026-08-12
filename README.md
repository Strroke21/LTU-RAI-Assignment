*** RTABMAP Launch Commands

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
```
ros2 run ltu-sensor-bridge ltu_sensors 

```