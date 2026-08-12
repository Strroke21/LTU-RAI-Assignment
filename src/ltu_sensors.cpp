#include <cstring>
#include <memory>
#include <string>
#include <vector>

#include <rclcpp/rclcpp.hpp>

#include <sensor_msgs/msg/imu.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <sensor_msgs/msg/camera_info.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <sensor_msgs/msg/point_field.hpp>

#include <gz/transport/Node.hh>

#include <gz/msgs/imu.pb.h>
#include <gz/msgs/image.pb.h>
#include <gz/msgs/camera_info.pb.h>
#include <gz/msgs/pointcloud_packed.pb.h>

class MultiSensorBridge : public rclcpp::Node
{
public:
    MultiSensorBridge()
        : Node("multi_sensor_bridge")
    {
        auto qos_sensor =
            rclcpp::QoS(rclcpp::KeepLast(10))
                .best_effort()
                .durability_volatile();

        //--------------------------------------------------
        // ZED2i #r0
        //--------------------------------------------------

        zed1_image_pub_ =
            create_publisher<sensor_msgs::msg::Image>(
                "/r0/zed2i/image", 1);

        zed1_depth_pub_ =
            create_publisher<sensor_msgs::msg::Image>(
                "/r0/zed2i/depth_image", 1);

        zed1_camera_pub_ =
            create_publisher<sensor_msgs::msg::CameraInfo>(
                "/r0/zed2i/camera_info", 1);

        zed1_imu_pub_ =
            create_publisher<sensor_msgs::msg::Imu>(
                "/r0/zed2i/imu", qos_sensor);

        zed1_cloud_pub_ =
            create_publisher<sensor_msgs::msg::PointCloud2>(
                "/r0/zed2i/points", qos_sensor);

        //--------------------------------------------------
        // ZED2i #r1
        //--------------------------------------------------

        zed2_image_pub_ =
            create_publisher<sensor_msgs::msg::Image>(
                "/r1/zed2i/image", 1);

        zed2_depth_pub_ =
            create_publisher<sensor_msgs::msg::Image>(
                "/r1/zed2i/depth_image", 1);

        zed2_camera_pub_ =
            create_publisher<sensor_msgs::msg::CameraInfo>(
                "/r1/zed2i/camera_info", 1);

        zed2_imu_pub_ =
            create_publisher<sensor_msgs::msg::Imu>(
                "/r1/zed2i/imu", qos_sensor);

        zed2_cloud_pub_ =
            create_publisher<sensor_msgs::msg::PointCloud2>(
                "/r1/zed2i/points", qos_sensor);

        //--------------------------------------------------
        // ZED2i #3
        //--------------------------------------------------

        zed3_image_pub_ =
            create_publisher<sensor_msgs::msg::Image>(
                "/r2/zed2i/image", 1);

        zed3_depth_pub_ =
            create_publisher<sensor_msgs::msg::Image>(
                "/r2/zed2i/depth_image", 1);

        zed3_camera_pub_ =
            create_publisher<sensor_msgs::msg::CameraInfo>(
                "/r2/zed2i/camera_info", 1);

        zed3_imu_pub_ =
            create_publisher<sensor_msgs::msg::Imu>(
                "/r2/zed2i/imu", qos_sensor);

        zed3_cloud_pub_ =
            create_publisher<sensor_msgs::msg::PointCloud2>(
                "/r2/zed2i/points", qos_sensor);

        //--------------------------------------------------
        // Livox
        //--------------------------------------------------

        livox1_pub_ =
            create_publisher<sensor_msgs::msg::PointCloud2>(
                "/r0/livox/points", qos_sensor);

        livox2_pub_ =
            create_publisher<sensor_msgs::msg::PointCloud2>(
                "/r1/livox/points", qos_sensor);

        livox3_pub_ =
            create_publisher<sensor_msgs::msg::PointCloud2>(
                "/r2/livox/points", qos_sensor);

        //--------------------------------------------------
        // Gazebo subscriptions
        //--------------------------------------------------

        // Livox #1
        gz_node_.Subscribe(
            "/ltu_livox1/points",
            &MultiSensorBridge::Livox1Callback,
            this);

        gz_node_.Subscribe(
            "/ltu_livox1/points/points",
            &MultiSensorBridge::Livox1Callback,
            this);

        // Livox #2
        gz_node_.Subscribe(
            "/ltu_livox2/points",
            &MultiSensorBridge::Livox2Callback,
            this);

        gz_node_.Subscribe(
            "/ltu_livox2/points/points",
            &MultiSensorBridge::Livox2Callback,
            this);

        // Livox #3
        gz_node_.Subscribe(
            "/ltu_livox3/points",
            &MultiSensorBridge::Livox3Callback,
            this);

        gz_node_.Subscribe(
            "/ltu_livox3/points/points",
            &MultiSensorBridge::Livox3Callback,
            this);

        //--------------------------------------------------
        // ZED1
        //--------------------------------------------------

        gz_node_.Subscribe("/ltu_zed2i_1/image",
                           &MultiSensorBridge::Zed1ImageCallback,
                           this);

        gz_node_.Subscribe("/ltu_zed2i_1/depth_image",
                           &MultiSensorBridge::Zed1DepthCallback,
                           this);

        gz_node_.Subscribe("/ltu_zed2i_1/camera_info",
                           &MultiSensorBridge::Zed1CameraInfoCallback,
                           this);

        gz_node_.Subscribe("/ltu_zed2i_1/imu",
                           &MultiSensorBridge::Zed1ImuCallback,
                           this);

        gz_node_.Subscribe("/ltu_zed2i_1/points",
                           &MultiSensorBridge::Zed1CloudCallback,
                           this);

        //--------------------------------------------------
        // ZED2
        //--------------------------------------------------

        gz_node_.Subscribe("/ltu_zed2i_2/image",
                           &MultiSensorBridge::Zed2ImageCallback,
                           this);

        gz_node_.Subscribe("/ltu_zed2i_2/depth_image",
                           &MultiSensorBridge::Zed2DepthCallback,
                           this);

        gz_node_.Subscribe("/ltu_zed2i_2/camera_info",
                           &MultiSensorBridge::Zed2CameraInfoCallback,
                           this);

        gz_node_.Subscribe("/ltu_zed2i_2/imu",
                           &MultiSensorBridge::Zed2ImuCallback,
                           this);

        gz_node_.Subscribe("/ltu_zed2i_2/points",
                           &MultiSensorBridge::Zed2CloudCallback,
                           this);

        //--------------------------------------------------
        // ZED3
        //--------------------------------------------------

        gz_node_.Subscribe("/ltu_zed2i_3/image",
                           &MultiSensorBridge::Zed3ImageCallback,
                           this);

        gz_node_.Subscribe("/ltu_zed2i_3/depth_image",
                           &MultiSensorBridge::Zed3DepthCallback,
                           this);

        gz_node_.Subscribe("/ltu_zed2i_3/camera_info",
                           &MultiSensorBridge::Zed3CameraInfoCallback,
                           this);

        gz_node_.Subscribe("/ltu_zed2i_3/imu",
                           &MultiSensorBridge::Zed3ImuCallback,
                           this);

        gz_node_.Subscribe("/ltu_zed2i_3/points",
                           &MultiSensorBridge::Zed3CloudCallback,
                           this);

        RCLCPP_INFO(get_logger(),
                    "Multi Sensor Bridge Started");
    }

private:

    //--------------------------------------------------
    // PointCloud conversion
    //--------------------------------------------------

    sensor_msgs::msg::PointCloud2 ConvertPointCloud(
        const gz::msgs::PointCloudPacked &msg)
    {
        sensor_msgs::msg::PointCloud2 ros_msg;

        ros_msg.header.stamp = now();

        ros_msg.height = msg.height();
        ros_msg.width = msg.width();

        ros_msg.point_step = msg.point_step();
        ros_msg.row_step = msg.row_step();

        ros_msg.is_bigendian = false;
        ros_msg.is_dense = false;

        ros_msg.data.resize(msg.data().size());

        memcpy(
            ros_msg.data.data(),
            msg.data().data(),
            msg.data().size());

        for (int i = 0; i < msg.field_size(); ++i)
        {
            sensor_msgs::msg::PointField field;

            field.name = msg.field(i).name();
            field.offset = msg.field(i).offset();
            field.count = msg.field(i).count();

            switch (msg.field(i).datatype())
            {
                case gz::msgs::PointCloudPacked::Field::FLOAT32:
                    field.datatype =
                        sensor_msgs::msg::PointField::FLOAT32;
                    break;

                case gz::msgs::PointCloudPacked::Field::FLOAT64:
                    field.datatype =
                        sensor_msgs::msg::PointField::FLOAT64;
                    break;

                case gz::msgs::PointCloudPacked::Field::UINT32:
                    field.datatype =
                        sensor_msgs::msg::PointField::UINT32;
                    break;

                default:
                    continue;
            }

            ros_msg.fields.push_back(field);
        }

        return ros_msg;
    }

    //--------------------------------------------------
    // IMU conversion
    //--------------------------------------------------

    sensor_msgs::msg::Imu ConvertImu(
        const gz::msgs::IMU &msg)
    {
        sensor_msgs::msg::Imu imu;

        imu.header.stamp = now();

        imu.orientation.x = msg.orientation().x();
        imu.orientation.y = msg.orientation().y();
        imu.orientation.z = msg.orientation().z();
        imu.orientation.w = msg.orientation().w();

        imu.angular_velocity.x =
            msg.angular_velocity().x();
        imu.angular_velocity.y =
            msg.angular_velocity().y();
        imu.angular_velocity.z =
            msg.angular_velocity().z();

        imu.linear_acceleration.x =
            msg.linear_acceleration().x();
        imu.linear_acceleration.y =
            msg.linear_acceleration().y();
        imu.linear_acceleration.z =
            msg.linear_acceleration().z();

        return imu;
    }

    //--------------------------------------------------
    // Livox callbacks
    //--------------------------------------------------

    void Livox1Callback(
        const gz::msgs::PointCloudPacked &msg)
    { livox1_pub_->publish(ConvertPointCloud(msg)); }

    void Livox2Callback(
        const gz::msgs::PointCloudPacked &msg)
    { livox2_pub_->publish(ConvertPointCloud(msg)); }

    void Livox3Callback(
        const gz::msgs::PointCloudPacked &msg)
    { livox3_pub_->publish(ConvertPointCloud(msg)); }

    //--------------------------------------------------
    // ZED IMU callbacks
    //--------------------------------------------------

    void Zed1ImuCallback(const gz::msgs::IMU &msg)
    { zed1_imu_pub_->publish(ConvertImu(msg)); }

    void Zed2ImuCallback(const gz::msgs::IMU &msg)
    { zed2_imu_pub_->publish(ConvertImu(msg)); }

    void Zed3ImuCallback(const gz::msgs::IMU &msg)
    { zed3_imu_pub_->publish(ConvertImu(msg)); }

    //--------------------------------------------------
    // Cloud callbacks
    //--------------------------------------------------

    void Zed1CloudCallback(
        const gz::msgs::PointCloudPacked &msg)
    { zed1_cloud_pub_->publish(ConvertPointCloud(msg)); }

    void Zed2CloudCallback(
        const gz::msgs::PointCloudPacked &msg)
    { zed2_cloud_pub_->publish(ConvertPointCloud(msg)); }

    void Zed3CloudCallback(
        const gz::msgs::PointCloudPacked &msg)
    { zed3_cloud_pub_->publish(ConvertPointCloud(msg)); }

    //--------------------------------------------------
    // IMAGE/CAMERA callbacks
    // implement same way depending on your
    // Gazebo message type
    //--------------------------------------------------

    void Zed1ImageCallback(const gz::msgs::Image &msg) {        
        sensor_msgs::msg::Image ros;
        builtin_interfaces::msg::Time t;
        ros.header.frame_id = "zed2i_camera";

        t.sec = msg.header().stamp().sec();
        t.nanosec = msg.header().stamp().nsec();
        ros.header.stamp = t;

        ros.height = msg.height();
        ros.width = msg.width();
        RCLCPP_INFO(get_logger(), "RGB: %d x %d", ros.width, ros.height);

        ros.encoding = "rgb8";

        ros.is_bigendian = false;

        ros.step = msg.step();

        ros.data.resize(msg.data().size());

        memcpy(
            ros.data.data(),
            msg.data().data(),
            msg.data().size());

        zed1_image_pub_->publish(ros);
    }

    void Zed2ImageCallback(const gz::msgs::Image &msg) {
                sensor_msgs::msg::Image ros;
        builtin_interfaces::msg::Time t;
        ros.header.frame_id = "zed2i_camera";

        t.sec = msg.header().stamp().sec();
        t.nanosec = msg.header().stamp().nsec();
        ros.header.stamp = t;

        ros.height = msg.height();
        ros.width = msg.width();
        RCLCPP_INFO(get_logger(), "RGB: %d x %d", ros.width, ros.height);

        ros.encoding = "rgb8";

        ros.is_bigendian = false;

        ros.step = msg.step();

        ros.data.resize(msg.data().size());

        memcpy(
            ros.data.data(),
            msg.data().data(),
            msg.data().size());

        zed2_image_pub_->publish(ros);
    }
    void Zed3ImageCallback(const gz::msgs::Image &msg) {
                sensor_msgs::msg::Image ros;
        builtin_interfaces::msg::Time t;
        ros.header.frame_id = "zed2i_camera";

        t.sec = msg.header().stamp().sec();
        t.nanosec = msg.header().stamp().nsec();
        ros.header.stamp = t;

        ros.height = msg.height();
        ros.width = msg.width();
        RCLCPP_INFO(get_logger(), "RGB: %d x %d", ros.width, ros.height);

        ros.encoding = "rgb8";

        ros.is_bigendian = false;

        ros.step = msg.step();

        ros.data.resize(msg.data().size());

        memcpy(
            ros.data.data(),
            msg.data().data(),
            msg.data().size());

        zed3_image_pub_->publish(ros);
    }

    void Zed1DepthCallback(const gz::msgs::Image &msg) {
        sensor_msgs::msg::Image ros;
        builtin_interfaces::msg::Time t;
        t.sec = msg.header().stamp().sec();
        t.nanosec = msg.header().stamp().nsec();
        ros.header.stamp = t;

        ros.header.frame_id = "zed2i_camera";

        ros.height = msg.height();
        ros.width = msg.width();
        RCLCPP_INFO(get_logger(), "Depth: %d x %d", ros.width, ros.height);

        switch (msg.pixel_format_type())
        {
        case gz::msgs::PixelFormatType::R_FLOAT32:
            ros.encoding = "32FC1";
            break;

        case gz::msgs::PixelFormatType::L_INT16:
            ros.encoding = "16UC1";
            break;

        default:
            ros.encoding = "32FC1";
            break;
        }

        ros.is_bigendian = false;

        ros.step = msg.step();

        ros.data.resize(msg.data().size());

        memcpy(
            ros.data.data(),
            msg.data().data(),
            msg.data().size());

        zed1_depth_pub_->publish(ros);
    }
    void Zed2DepthCallback(const gz::msgs::Image &msg) {
        sensor_msgs::msg::Image ros;
        builtin_interfaces::msg::Time t;
        t.sec = msg.header().stamp().sec();
        t.nanosec = msg.header().stamp().nsec();
        ros.header.stamp = t;

        ros.header.frame_id = "zed2i_camera";

        ros.height = msg.height();
        ros.width = msg.width();
        RCLCPP_INFO(get_logger(), "Depth: %d x %d", ros.width, ros.height);

        switch (msg.pixel_format_type())
        {
        case gz::msgs::PixelFormatType::R_FLOAT32:
            ros.encoding = "32FC1";
            break;

        case gz::msgs::PixelFormatType::L_INT16:
            ros.encoding = "16UC1";
            break;

        default:
            ros.encoding = "32FC1";
            break;
        }

        ros.is_bigendian = false;

        ros.step = msg.step();

        ros.data.resize(msg.data().size());

        memcpy(
            ros.data.data(),
            msg.data().data(),
            msg.data().size());

        zed2_depth_pub_->publish(ros);
    }
    void Zed3DepthCallback(const gz::msgs::Image &msg) {
        sensor_msgs::msg::Image ros;
        builtin_interfaces::msg::Time t;
        t.sec = msg.header().stamp().sec();
        t.nanosec = msg.header().stamp().nsec();
        ros.header.stamp = t;

        ros.header.frame_id = "zed2i_camera";

        ros.height = msg.height();
        ros.width = msg.width();
        RCLCPP_INFO(get_logger(), "Depth: %d x %d", ros.width, ros.height);

        switch (msg.pixel_format_type())
        {
        case gz::msgs::PixelFormatType::R_FLOAT32:
            ros.encoding = "32FC1";
            break;

        case gz::msgs::PixelFormatType::L_INT16:
            ros.encoding = "16UC1";
            break;

        default:
            ros.encoding = "32FC1";
            break;
        }

        ros.is_bigendian = false;

        ros.step = msg.step();

        ros.data.resize(msg.data().size());

        memcpy(
            ros.data.data(),
            msg.data().data(),
            msg.data().size());

        zed3_depth_pub_->publish(ros);
    }

    void Zed1CameraInfoCallback(
        const gz::msgs::CameraInfo &msg) {
            sensor_msgs::msg::CameraInfo ros; 
        builtin_interfaces::msg::Time t;
        t.sec = msg.header().stamp().sec();
        t.nanosec = msg.header().stamp().nsec();
        ros.header.stamp = t;
        ros.header.frame_id = "zed2i_camera";
        ros.width = msg.width(); 
        ros.height = msg.height();
        double width = 1280.0;
        double height = 720.0;
        double hfov = 1.91986;

        double fx = width / (2.0 * std::tan(hfov / 2.0));
        double fy = fx;                  // assuming square pixels
        double cx = width / 2.0;
        double cy = height / 2.0;

        ros.k = {
          fx, 0, cx,
          0, fy, cy,
          0, 0, 1
          };

        ros.p = {
            fx, 0, cx, 0,
            0, fy, cy, 0,
            0, 0, 1, 0
        };

        ros.r = {
            1,0,0,
            0,1,0,
            0,0,1
        };

        zed1_camera_pub_->publish(ros);
        }

    void Zed2CameraInfoCallback(
        const gz::msgs::CameraInfo &msg) {
            sensor_msgs::msg::CameraInfo ros; 
        builtin_interfaces::msg::Time t;
        t.sec = msg.header().stamp().sec();
        t.nanosec = msg.header().stamp().nsec();
        ros.header.stamp = t;
        ros.header.frame_id = "zed2i_camera";
        ros.width = msg.width(); 
        ros.height = msg.height();
        double width = 1280.0;
        double height = 720.0;
        double hfov = 1.91986;

        double fx = width / (2.0 * std::tan(hfov / 2.0));
        double fy = fx;                  // assuming square pixels
        double cx = width / 2.0;
        double cy = height / 2.0;

        ros.k = {
          fx, 0, cx,
          0, fy, cy,
          0, 0, 1
          };

        ros.p = {
            fx, 0, cx, 0,
            0, fy, cy, 0,
            0, 0, 1, 0
        };

        ros.r = {
            1,0,0,
            0,1,0,
            0,0,1
        };

        zed2_camera_pub_->publish(ros);
        }

    void Zed3CameraInfoCallback(
        const gz::msgs::CameraInfo &msg) {
        sensor_msgs::msg::CameraInfo ros; 
        builtin_interfaces::msg::Time t;
        t.sec = msg.header().stamp().sec();
        t.nanosec = msg.header().stamp().nsec();
        ros.header.stamp = t;
        ros.header.frame_id = "zed2i_camera";
        ros.width = msg.width(); 
        ros.height = msg.height();
        double width = 1280.0;
        double height = 720.0;
        double hfov = 1.91986;

        double fx = width / (2.0 * std::tan(hfov / 2.0));
        double fy = fx;                  // assuming square pixels
        double cx = width / 2.0;
        double cy = height / 2.0;

        ros.k = {
          fx, 0, cx,
          0, fy, cy,
          0, 0, 1
          };

        ros.p = {
            fx, 0, cx, 0,
            0, fy, cy, 0,
            0, 0, 1, 0
        };

        ros.r = {
            1,0,0,
            0,1,0,
            0,0,1
        };

        zed3_camera_pub_->publish(ros);}

    //--------------------------------------------------

    gz::transport::Node gz_node_;

    rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr
        livox1_pub_, livox2_pub_, livox3_pub_;

    rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr
        zed1_imu_pub_, zed2_imu_pub_, zed3_imu_pub_;

    rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr
        zed1_cloud_pub_, zed2_cloud_pub_, zed3_cloud_pub_;

    rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr
        zed1_image_pub_, zed2_image_pub_, zed3_image_pub_;

    rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr
        zed1_depth_pub_, zed2_depth_pub_, zed3_depth_pub_;

    rclcpp::Publisher<sensor_msgs::msg::CameraInfo>::SharedPtr
        zed1_camera_pub_, zed2_camera_pub_, zed3_camera_pub_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);

    rclcpp::spin(
        std::make_shared<MultiSensorBridge>());

    rclcpp::shutdown();
    return 0;
}
