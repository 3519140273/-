cmake_minimum_required(VERSION 3.0.2)
project(car_description)

# 只保留Noetic必需的依赖（删除冗余避免编译报错）
find_package(catkin REQUIRED COMPONENTS
  rospy
  urdf
  xacro
  robot_state_publisher
  gazebo_ros
)

catkin_package(
  CATKIN_DEPENDS rospy urdf xacro gazebo_ros
)

include_directories(${catkin_INCLUDE_DIRS})

# 安装Python控制脚本
catkin_install_python(PROGRAMS
  scripts/car_teleop.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
