#!/bin/bash
PKG=~/catkin_ws/src/my_robot

# ==== package.xml ====
cat > $PKG/package.xml <<'EOF'
<?xml version="1.0"?>
<package format="2">
  <name>my_robot</name>
  <version>0.0.1</version>
  <description>实验二：建图和自主导航</description>
  <maintainer email="user@todo.todo">user</maintainer>
  <license>TODO</license>
  <buildtool_depend>catkin</buildtool_depend>
  <depend>roscpp</depend>
  <depend>rospy</depend>
  <depend>std_msgs</depend>
  <depend>sensor_msgs</depend>
  <depend>geometry_msgs</depend>
  <depend>nav_msgs</depend>
  <depend>tf</depend>
  <depend>gazebo_ros</depend>
  <depend>urdf</depend>
  <depend>xacro</depend>
  <depend>joint_state_publisher</depend>
  <depend>robot_state_publisher</depend>
  <export>
    <gazebo_ros gazebo_model_path="${prefix}/urdf"/>
  </export>
</package>
EOF

# ==== CMakeLists.txt ====
cat > $PKG/CMakeLists.txt <<'EOF'
cmake_minimum_required(VERSION 3.0.2)
project(my_robot)
find_package(catkin REQUIRED COMPONENTS
  roscpp rospy std_msgs sensor_msgs geometry_msgs nav_msgs tf
)
catkin_package()
include_directories(${catkin_INCLUDE_DIRS})
install(DIRECTORY launch/ DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch)
install(DIRECTORY urdf/   DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/urdf)
install(DIRECTORY config/ DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/config)
install(DIRECTORY worlds/ DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/worlds)
install(DIRECTORY maps/   DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/maps)
EOF

# ==== urdf/my_robot.urdf (4-wheel) ====
cat > $PKG/urdf/my_robot.urdf <<'''ENDOFFILE'''
<?xml version="1.0"?>
<robot name="my_robot">

  <material name="black"><color rgba="0.0 0.0 0.0 1.0"/></material>
  <material name="blue"><color rgba="0.0 0.0 1.0 1.0"/></material>
  <material name="green"><color rgba="0.0 1.0 0.0 1.0"/></material>
  <material name="red"><color rgba="1.0 0.0 0.0 1.0"/></material>
  <material name="grey"><color rgba="0.5 0.5 0.5 1.0"/></material>

  <!-- ===== 0. 地面投影 ===== -->
  <link name="base_footprint"/>

  <!-- ===== 1. 底盘 ===== -->
  <link name="base_link">
    <visual>
      <origin xyz="0 0 0.085" rpy="0 0 0"/>
      <geometry><box size="0.40 0.25 0.17"/></geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0 0 0.085" rpy="0 0 0"/>
      <geometry><box size="0.40 0.25 0.17"/></geometry>
    </collision>
    <inertial>
      <mass value="10.0"/>
      <origin xyz="0 0 0.085"/>
      <inertia ixx="0.20" iyy="0.20" izz="0.35" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

  <joint name="base_joint" type="fixed">
    <parent link="base_footprint"/>
    <child  link="base_link"/>
    <origin xyz="0 0 0"/>
  </joint>

  <!-- ============================================ -->
  <!--  左前驱动轮 (x=+0.14, y=+0.17, r=0.065)      -->
  <!-- ============================================ -->
  <link name="lf_wheel">
    <visual>
      <origin xyz="0 0 0" rpy="1.5708 0 0"/>
      <geometry><cylinder length="0.04" radius="0.065"/></geometry>
      <material name="black"/>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry><cylinder length="0.04" radius="0.065"/></geometry>
    </collision>
    <inertial>
      <mass value="0.3"/>
      <inertia ixx="0.0004" iyy="0.0004" izz="0.0006" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

  <joint name="lf_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child  link="lf_wheel"/>
    <origin xyz="0.14 0.17 0.065" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit effort="100" velocity="10"/>
    <dynamics damping="0.1" friction="1.0"/>
  </joint>

  <!-- ============================================ -->
  <!--  右前驱动轮 (x=+0.14, y=-0.17, r=0.065)      -->
  <!-- ============================================ -->
  <link name="rf_wheel">
    <visual>
      <origin xyz="0 0 0" rpy="1.5708 0 0"/>
      <geometry><cylinder length="0.04" radius="0.065"/></geometry>
      <material name="black"/>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry><cylinder length="0.04" radius="0.065"/></geometry>
    </collision>
    <inertial>
      <mass value="0.3"/>
      <inertia ixx="0.0004" iyy="0.0004" izz="0.0006" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

  <joint name="rf_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child  link="rf_wheel"/>
    <origin xyz="0.14 -0.17 0.065" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit effort="100" velocity="10"/>
    <dynamics damping="0.1" friction="1.0"/>
  </joint>

  <!-- ============================================ -->
  <!--  左后从动轮 (x=-0.14, y=+0.17, r=0.065)      -->
  <!-- ============================================ -->
  <link name="lr_wheel">
    <visual>
      <origin xyz="0 0 0" rpy="1.5708 0 0"/>
      <geometry><cylinder length="0.04" radius="0.065"/></geometry>
      <material name="grey"/>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry><cylinder length="0.04" radius="0.065"/></geometry>
    </collision>
    <inertial>
      <mass value="0.3"/>
      <inertia ixx="0.0004" iyy="0.0004" izz="0.0006" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

  <joint name="lr_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child  link="lr_wheel"/>
    <origin xyz="-0.14 0.17 0.065" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <dynamics damping="0.05" friction="0.5"/>
  </joint>

  <!-- ============================================ -->
  <!--  右后从动轮 (x=-0.14, y=-0.17, r=0.065)      -->
  <!-- ============================================ -->
  <link name="rr_wheel">
    <visual>
      <origin xyz="0 0 0" rpy="1.5708 0 0"/>
      <geometry><cylinder length="0.04" radius="0.065"/></geometry>
      <material name="grey"/>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry><cylinder length="0.04" radius="0.065"/></geometry>
    </collision>
    <inertial>
      <mass value="0.3"/>
      <inertia ixx="0.0004" iyy="0.0004" izz="0.0006" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

  <joint name="rr_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child  link="rr_wheel"/>
    <origin xyz="-0.14 -0.17 0.065" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <dynamics damping="0.05" friction="0.5"/>
  </joint>

  <!-- ===== LIDAR ===== -->
  <link name="lidar_link">
    <visual>
      <geometry><cylinder length="0.03" radius="0.04"/></geometry>
      <material name="red"/>
    </visual>
    <collision>
      <geometry><cylinder length="0.03" radius="0.04"/></geometry>
    </collision>
    <inertial>
      <mass value="0.05"/>
      <inertia ixx="0.00001" iyy="0.00001" izz="0.00001" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

  <joint name="lidar_joint" type="fixed">
    <parent link="base_link"/>
    <child  link="lidar_link"/>
    <origin xyz="0.18 0 0.19" rpy="0 0 0"/>
  </joint>

  <gazebo reference="lidar_link">
    <sensor type="ray" name="lds_lidar">
      <pose>0 0 0 0 0 0</pose>
      <visualize>false</visualize>
      <update_rate>10</update_rate>
      <ray>
        <scan>
          <horizontal>
            <samples>360</samples>
            <resolution>1</resolution>
            <min_angle>-1.570796</min_angle>
            <max_angle>1.570796</max_angle>
          </horizontal>
        </scan>
        <range>
          <min>0.12</min>
          <max>10.0</max>
          <resolution>0.01</resolution>
        </range>
        <noise>
          <type>gaussian</type>
          <mean>0.0</mean>
          <stddev>0.01</stddev>
        </noise>
      </ray>
      <plugin name="gazebo_ros_lds_lidar" filename="libgazebo_ros_laser.so">
        <topicName>/scan</topicName>
        <frameName>lidar_link</frameName>
      </plugin>
    </sensor>
  </gazebo>

  <!-- ===== RGB 摄像头 ===== -->
  <link name="camera_link">
    <visual>
      <geometry><box size="0.03 0.06 0.03"/></geometry>
      <material name="green"/>
    </visual>
    <collision>
      <geometry><box size="0.03 0.06 0.03"/></geometry>
    </collision>
    <inertial>
      <mass value="0.02"/>
      <inertia ixx="0.00001" iyy="0.00001" izz="0.00001" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

  <joint name="camera_joint" type="fixed">
    <parent link="base_link"/>
    <child  link="camera_link"/>
    <origin xyz="0.22 0 0.22" rpy="0 0 0"/>
  </joint>

  <gazebo reference="camera_link">
    <sensor type="camera" name="rgb_camera">
      <update_rate>30.0</update_rate>
      <camera>
        <horizontal_fov>1.047198</horizontal_fov>
        <image>
          <width>640</width>
          <height>480</height>
          <format>R8G8B8</format>
        </image>
        <clip>
          <near>0.05</near>
          <far>10.0</far>
        </clip>
      </camera>
      <plugin name="gazebo_ros_camera" filename="libgazebo_ros_camera.so">
        <alwaysOn>true</alwaysOn>
        <updateRate>30.0</updateRate>
        <imageTopicName>/camera/rgb/image_raw</imageTopicName>
        <cameraInfoTopicName>/camera/rgb/camera_info</cameraInfoTopicName>
        <frameName>camera_link</frameName>
        <hackBaseline>0.07</hackBaseline>
        <distortionK1>0.0</distortionK1>
        <distortionK2>0.0</distortionK2>
        <distortionK3>0.0</distortionK3>
        <distortionT1>0.0</distortionT1>
        <distortionT2>0.0</distortionT2>
      </plugin>
    </sensor>
  </gazebo>

  <!-- ===== 差速驱动 (只控前面两个驱动轮) ===== -->
  <gazebo>
    <plugin name="gazebo_ros_diff_drive" filename="libgazebo_ros_diff_drive.so">
      <numWheelPairs>1</numWheelPairs>
      <leftJoint>lf_wheel_joint</leftJoint>
      <rightJoint>rf_wheel_joint</rightJoint>
      <wheelSeparation>0.34</wheelSeparation>
      <wheelDiameter>0.13</wheelDiameter>
      <wheelTorque>50</wheelTorque>
      <wheelAcceleration>2.0</wheelAcceleration>
      <commandTopic>/cmd_vel</commandTopic>
      <odometryTopic>/odom</odometryTopic>
      <odometryFrame>odom</odometryFrame>
      <robotBaseFrame>base_footprint</robotBaseFrame>
      <publishWheelTF>false</publishWheelTF>
      <publishOdomTF>true</publishOdomTF>
      <publishWheelJointState>true</publishWheelJointState>
      <updateRate>100.0</updateRate>
    </plugin>
  </gazebo>

  <gazebo>
    <plugin name="joint_state_publisher" filename="libgazebo_ros_joint_state_publisher.so">
      <updateRate>100.0</updateRate>
    </plugin>
  </gazebo>

</robot>

ENDOFFILE

# ==== worlds/room.world ====
cat > $PKG/worlds/room.world <<'EOF'
<?xml version="1.0"?>
<sdf version="1.6">
  <world name="room_world">
    <include><uri>model://sun</uri></include>
    <model name="ground_plane"><static>true</static>
      <link name="link">
        <collision name="collision"><geometry><plane><normal>0 0 1</normal><size>20 20</size></plane></geometry></collision>
        <visual name="visual"><geometry><plane><normal>0 0 1</normal><size>20 20</size></plane></geometry>
          <material><ambient>0.3 0.3 0.3 1</ambient><diffuse>0.7 0.7 0.7 1</diffuse><specular>0.01 0.01 0.01 1</specular></material></visual>
      </link>
    </model>
    <model name="wall_north"><static>true</static><pose>0 5 1.25 0 0 0</pose><link name="link"><collision name="collision"><geometry><box><size>10 0.2 2.5</size></box></geometry></collision><visual name="visual"><geometry><box><size>10 0.2 2.5</size></box></geometry><material><ambient>0.2 0.2 0.2 1</ambient><diffuse>0.5 0.5 0.5 1</diffuse></material></visual></link></model>
    <model name="wall_south"><static>true</static><pose>0 -5 1.25 0 0 0</pose><link name="link"><collision name="collision"><geometry><box><size>10 0.2 2.5</size></box></geometry></collision><visual name="visual"><geometry><box><size>10 0.2 2.5</size></box></geometry><material><ambient>0.2 0.2 0.2 1</ambient><diffuse>0.5 0.5 0.5 1</diffuse></material></visual></link></model>
    <model name="wall_east"><static>true</static><pose>5 0 1.25 0 0 0</pose><link name="link"><collision name="collision"><geometry><box><size>0.2 10 2.5</size></box></geometry></collision><visual name="visual"><geometry><box><size>0.2 10 2.5</size></box></geometry><material><ambient>0.2 0.2 0.2 1</ambient><diffuse>0.5 0.5 0.5 1</diffuse></material></visual></link></model>
    <model name="wall_west"><static>true</static><pose>-5 0 1.25 0 0 0</pose><link name="link"><collision name="collision"><geometry><box><size>0.2 10 2.5</size></box></geometry></collision><visual name="visual"><geometry><box><size>0.2 10 2.5</size></box></geometry><material><ambient>0.2 0.2 0.2 1</ambient><diffuse>0.5 0.5 0.5 1</diffuse></material></visual></link></model>
    <model name="obstacle_1"><static>true</static><pose>1.5 1.5 0.5 0 0 0</pose><link name="link"><collision name="collision"><geometry><box><size>0.8 0.8 1.0</size></box></geometry></collision><visual name="visual"><geometry><box><size>0.8 0.8 1.0</size></box></geometry><material><ambient>0.8 0.4 0.2 1</ambient><diffuse>0.9 0.5 0.3 1</diffuse></material></visual></link></model>
    <model name="obstacle_2"><static>true</static><pose>-2 1 0.5 0 0 0</pose><link name="link"><collision name="collision"><geometry><box><size>0.6 0.6 1.0</size></box></geometry></collision><visual name="visual"><geometry><box><size>0.6 0.6 1.0</size></box></geometry><material><ambient>0.2 0.4 0.8 1</ambient><diffuse>0.3 0.5 0.9 1</diffuse></material></visual></link></model>
    <model name="obstacle_3"><static>true</static><pose>-1.5 -2 0.5 0 0 0</pose><link name="link"><collision name="collision"><geometry><cylinder><radius>0.35</radius><length>1.0</length></cylinder></geometry></collision><visual name="visual"><geometry><cylinder><radius>0.35</radius><length>1.0</length></cylinder></geometry><material><ambient>0.2 0.6 0.3 1</ambient><diffuse>0.3 0.7 0.4 1</diffuse></material></visual></link></model>
    <model name="obstacle_4"><static>true</static><pose>3 -1 0.5 0 0 0</pose><link name="link"><collision name="collision"><geometry><box><size>0.6 1.0 1.0</size></box></geometry></collision><visual name="visual"><geometry><box><size>0.6 1.0 1.0</size></box></geometry><material><ambient>0.6 0.5 0.2 1</ambient><diffuse>0.7 0.6 0.3 1</diffuse></material></visual></link></model>
  </world>
</sdf>
EOF

# ==== launch/gazebo.launch ====
cat > $PKG/launch/gazebo.launch <<'EOF'
<launch>
  <param name="/use_sim_time" value="true"/>
  <include file="$(find gazebo_ros)/launch/empty_world.launch">
    <arg name="world_name" value="$(find my_robot)/worlds/room.world"/>
    <arg name="paused" value="false"/>
    <arg name="use_sim_time" value="true"/>
    <arg name="gui" value="true"/>
    <arg name="headless" value="false"/>
    <arg name="debug" value="false"/>
  </include>
  <param name="robot_description" command="$(find xacro)/xacro --inorder $(find my_robot)/urdf/my_robot.urdf"/>
  <node name="spawn_urdf" pkg="gazebo_ros" type="spawn_model" args="-param robot_description -urdf -model my_robot -x 0 -y 0 -z 0.1" output="screen"/>
  <node name="robot_state_publisher" pkg="robot_state_publisher" type="robot_state_publisher"><param name="publish_frequency" value="50.0"/></node>
  <node name="teleop_keyboard" pkg="teleop_twist_keyboard" type="teleop_twist_keyboard.py" launch-prefix="xterm -e" output="screen"><remap from="/cmd_vel" to="/cmd_vel"/></node>
</launch>
EOF

# ==== launch/gmapping.launch ====
cat > $PKG/launch/gmapping.launch <<'EOF'
<launch>
  <param name="/use_sim_time" value="true"/>
  <node name="gmapping" pkg="gmapping" type="slam_gmapping" output="screen">
    <param name="base_frame" value="base_footprint"/>
    <param name="odom_frame" value="odom"/>
    <param name="map_frame" value="map"/>
    <param name="map_update_interval" value="1.0"/>
    <param name="maxUrange" value="10.0"/>
    <param name="maxRange" value="15.0"/>
    <param name="sigma" value="0.05"/>
    <param name="kernelSize" value="1"/>
    <param name="lstep" value="0.05"/>
    <param name="astep" value="0.05"/>
    <param name="iterations" value="5"/>
    <param name="lsigma" value="0.075"/>
    <param name="ogain" value="3.0"/>
    <param name="lskip" value="0"/>
    <param name="minimumScore" value="50"/>
    <param name="srr" value="0.01"/>
    <param name="srt" value="0.02"/>
    <param name="str" value="0.01"/>
    <param name="stt" value="0.02"/>
    <param name="linearUpdate" value="0.5"/>
    <param name="angularUpdate" value="0.44"/>
    <param name="temporalUpdate" value="-1.0"/>
    <param name="resampleThreshold" value="0.5"/>
    <param name="particles" value="80"/>
    <param name="xmin" value="-10"/><param name="ymin" value="-10"/>
    <param name="xmax" value="10"/><param name="ymax" value="10"/>
    <param name="delta" value="0.05"/>
    <param name="occ_thresh" value="0.25"/>
  </node>
</launch>
EOF

# ==== launch/amcl_navigation.launch ====
cat > $PKG/launch/amcl_navigation.launch <<'EOF'
<launch>
  <param name="/use_sim_time" value="true"/>
  <node name="amcl" pkg="amcl" type="amcl" output="screen">
    <param name="odom_model_type" value="diff"/>
    <param name="odom_alpha1" value="0.2"/>
    <param name="odom_alpha2" value="0.2"/>
    <param name="odom_alpha3" value="0.2"/>
    <param name="odom_alpha4" value="0.2"/>
    <param name="laser_model_type" value="likelihood_field"/>
    <param name="laser_likelihood_max_dist" value="2.0"/>
    <param name="laser_max_beams" value="30"/>
    <param name="min_particles" value="500"/>
    <param name="max_particles" value="5000"/>
    <param name="kld_err" value="0.05"/>
    <param name="kld_z" value="0.99"/>
    <param name="update_min_d" value="0.05"/>
    <param name="update_min_a" value="0.05"/>
    <param name="resample_interval" value="1"/>
    <param name="transform_tolerance" value="0.5"/>
    <param name="recovery_alpha_slow" value="0.0"/>
    <param name="recovery_alpha_fast" value="0.0"/>
    <param name="gui_publish_rate" value="10.0"/>
    <param name="initial_pose_x" value="0.0"/>
    <param name="initial_pose_y" value="0.0"/>
    <param name="initial_pose_a" value="0.0"/>
    <param name="use_map_topic" value="true"/>
    <param name="first_map_only" value="false"/>
  </node>
  <node name="move_base" pkg="move_base" type="move_base" output="screen">
    <rosparam file="$(find my_robot)/config/costmap_common.yaml" command="load" ns="global_costmap"/>
    <rosparam file="$(find my_robot)/config/costmap_common.yaml" command="load" ns="local_costmap"/>
    <rosparam file="$(find my_robot)/config/global_costmap.yaml" command="load"/>
    <rosparam file="$(find my_robot)/config/local_costmap.yaml" command="load"/>
    <rosparam file="$(find my_robot)/config/dwa_planner.yaml" command="load"/>
    <rosparam file="$(find my_robot)/config/move_base.yaml" command="load"/>
  </node>
</launch>
EOF

# ==== launch/map_server.launch ====
cat > $PKG/launch/map_server.launch <<'EOF'
<launch>
  <param name="/use_sim_time" value="true"/>
  <node name="map_server" pkg="map_server" type="map_server" args="$(find my_robot)/maps/my_map.yaml"/>
</launch>
EOF

# ==== launch/map_saver.launch ====
cat > $PKG/launch/map_saver.launch <<'EOF'
<launch>
  <node name="map_saver" pkg="map_server" type="map_saver" args="-f $(find my_robot)/maps/my_map"><param name="occ_thresh" value="0.65"/></node>
</launch>
EOF

# ==== config/costmap_common.yaml ====
cat > $PKG/config/costmap_common.yaml <<'EOF'
obstacle_range: 3.0
raytrace_range: 4.0
robot_radius: 0.26
inflation_radius: 0.55
observation_sources: laser_scan_sensor
laser_scan_sensor:
  sensor_frame: lidar_link
  data_type: LaserScan
  topic: /scan
  marking: true
  clearing: true
  min_obstacle_height: 0.0
  max_obstacle_height: 2.0
EOF

# ==== config/global_costmap.yaml ====
cat > $PKG/config/global_costmap.yaml <<'EOF'
global_costmap:
  global_frame: map
  robot_base_frame: base_footprint
  update_frequency: 5.0
  publish_frequency: 2.0
  static_map: true
  rolling_window: false
  transform_tolerance: 0.5
  plugins:
    - {name: static_layer,    type: "costmap_2d::StaticLayer"}
    - {name: obstacle_layer,  type: "costmap_2d::ObstacleLayer"}
    - {name: inflation_layer, type: "costmap_2d::InflationLayer"}
EOF

# ==== config/local_costmap.yaml ====
cat > $PKG/config/local_costmap.yaml <<'EOF'
local_costmap:
  global_frame: odom
  robot_base_frame: base_footprint
  update_frequency: 5.0
  publish_frequency: 2.0
  static_map: false
  rolling_window: true
  width: 4.0
  height: 4.0
  resolution: 0.05
  transform_tolerance: 0.5
  plugins:
    - {name: obstacle_layer,  type: "costmap_2d::ObstacleLayer"}
    - {name: inflation_layer, type: "costmap_2d::InflationLayer"}
EOF

# ==== config/dwa_planner.yaml ====
cat > $PKG/config/dwa_planner.yaml <<'EOF'
DWAPlannerROS:
  max_vel_x: 0.8
  min_vel_x: -0.3
  max_vel_theta: 2.0
  min_vel_theta: -2.0
  min_in_place_vel_theta: 0.6
  acc_lim_x: 2.0
  acc_lim_theta: 3.0
  xy_goal_tolerance: 0.15
  yaw_goal_tolerance: 0.15
  sim_time: 1.5
  sim_granularity: 0.025
  vx_samples: 10
  vtheta_samples: 20
  path_distance_bias: 32.0
  goal_distance_bias: 24.0
  occdist_scale: 0.01
  forward_point_distance: 0.325
  stop_time_buffer: 0.2
  scaling_speed: 0.25
  max_scaling_factor: 0.2
  oscillation_reset_dist: 0.05
  publish_cost_grid_pc: false
EOF

# ==== config/move_base.yaml ====
cat > $PKG/config/move_base.yaml <<'EOF'
shutdown_costmaps: false
controller_frequency: 10.0
controller_patience: 5.0
planner_frequency: 2.0
planner_patience: 5.0
oscillation_timeout: 10.0
oscillation_distance: 0.2
base_global_planner: "navfn/NavfnROS"
base_local_planner: "dwa_local_planner/DWAPlannerROS"
recovery_behavior_enabled: true
clearing_rotation_allowed: true
recovery_behaviors:
  - name: 'conservative_reset'
    type: 'clear_costmap_recovery/ClearCostmapRecovery'
  - name: 'rotate_recovery'
    type: 'rotate_recovery/RotateRecovery'
  - name: 'aggressive_reset'
    type: 'clear_costmap_recovery/ClearCostmapRecovery'
conservative_reset:
  reset_distance: 1.0
aggressive_reset:
  reset_distance: 3.0
EOF

echo "===================================="
echo "  全部文件创建完成！"
echo "===================================="
find $PKG -type f | sort

