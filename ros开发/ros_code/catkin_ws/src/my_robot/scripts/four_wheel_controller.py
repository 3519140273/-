#!/usr/bin/env python3
import rospy
import math
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Twist

class FourWheelController:
    def __init__(self):
        rospy.init_node('four_wheel_controller')
        self.wheel_radius = 0.08
        self.wheel_base = 0.36
        self.wheel_track = 0.36
        self.rear_left_pos = 0.0
        self.rear_right_pos = 0.0
        self.front_left_pos = 0.0
        self.front_right_pos = 0.0
        self.steer_left_pos = 0.0
        self.steer_right_pos = 0.0
        self.last_time = rospy.Time.now()

        rospy.Subscriber('/cmd_vel', Twist, self.cmd_vel_callback)
        self.joint_pub = rospy.Publisher('/joint_states', JointState, queue_size=10)
        self.publish_state(rospy.Time.now())
        rospy.Timer(rospy.Duration(0.05), self.timer_callback)
        rospy.loginfo("四轮控制器启动，等待 /cmd_vel ...")

    def publish_state(self, stamp):
        js = JointState()
        js.header.stamp = stamp
        js.name = [
            'rear_left_wheel_joint', 'rear_right_wheel_joint',
            'front_left_wheel_joint', 'front_right_wheel_joint',
            'front_left_steer_joint', 'front_right_steer_joint',
        ]
        js.position = [
            self.rear_left_pos, self.rear_right_pos,
            self.front_left_pos, self.front_right_pos,
            self.steer_left_pos, self.steer_right_pos,
        ]
        self.joint_pub.publish(js)

    def timer_callback(self, event):
        self.publish_state(rospy.Time.now())

    def cmd_vel_callback(self, msg):
        now = rospy.Time.now()
        dt = (now - self.last_time).to_sec()
        if dt <= 0: dt = 0.02
        self.last_time = now
        v, w = msg.linear.x, msg.angular.z
        vl = (v - w * self.wheel_base / 2.0) / self.wheel_radius
        vr = (v + w * self.wheel_base / 2.0) / self.wheel_radius
        self.rear_left_pos += vl * dt
        self.rear_right_pos += vr * dt
        self.front_left_pos += vl * dt
        self.front_right_pos += vr * dt
        if abs(v) > 0.01:
            sa = math.atan2(self.wheel_track * w, v)
            sa = max(-0.6, min(0.6, sa))
        else:
            sa = 0.3 * w
            sa = max(-0.6, min(0.6, sa))
        self.steer_left_pos = sa
        self.steer_right_pos = sa

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    FourWheelController().run()
