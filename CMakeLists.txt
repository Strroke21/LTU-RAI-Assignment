cmake_minimum_required(VERSION 3.10)
project(ltu-sensor-bridge)

set(CMAKE_CXX_STANDARD 17)

# Gazebo
find_package(gz-transport12 REQUIRED)
find_package(gz-msgs9 REQUIRED)

# ROS2
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(cv_bridge REQUIRED)

# OpenCV
find_package(OpenCV REQUIRED)
#==============================
# LTU bridge
#==============================

add_executable(ltu_sensors src/ltu_sensors.cpp)
ament_target_dependencies(ltu_sensors
    rclcpp
    sensor_msgs
    cv_bridge
)

target_include_directories(ltu_sensors PUBLIC
    ${OpenCV_INCLUDE_DIRS}
)
target_link_libraries(ltu_sensors
    gz-transport12::core
    gz-msgs9::core
)

# ----------------------

install(TARGETS
    ltu_sensors
    DESTINATION lib/${PROJECT_NAME}
)
ament_package()
