#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64

class CarTeleop:
    def __init__(self):
        rospy.init_node('car_teleop')
        self.wheel_radius = 0.08
        self.pub_lr = rospy.Publisher('/left_rear_wheel_joint/command', Float64, queue_size=10)
        self.pub_rr = rospy.Publisher('/right_rear_wheel_joint/command', Float64, queue_size=10)
        self.pub_ls = rospy.Publisher('/left_front_steering_joint/command', Float64, queue_size=10)
        self.pub_rs = rospy.Publisher('/right_front_steering_joint/command', Float64, queue_size=10)
        rospy.Subscriber("/cmd_vel", Twist, self.cb)
        rospy.spin()

    def cb(self, msg):
        speed = msg.linear.x / self.wheel_radius
        steer = max(-0.785, min(0.785, msg.angular.z * 0.6))
        self.pub_lr.publish(speed)
        self.pub_rr.publish(speed)
        self.pub_ls.publish(steer)
        self.pub_rs.publish(steer)

if __name__ == "__main__":
    try:
        CarTeleop()
    except rospy.ROSInterruptException:
        pass
