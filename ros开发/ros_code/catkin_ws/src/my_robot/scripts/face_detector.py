#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

class FaceDetector:
    def __init__(self):
        rospy.init_node('face_detector', anonymous=True)
        self.bridge = CvBridge()
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            rospy.logerr("无法加载 Haar Cascade: %s", cascade_path)
            return
        rospy.loginfo("人脸检测器初始化完成")
        self.image_sub = rospy.Subscriber(
            '/camera/rgb/image_raw', Image, self.image_callback, queue_size=1)
        self.image_pub = rospy.Publisher(
            '/face_detection/result', Image, queue_size=1)
        rospy.loginfo("已订阅: /camera/rgb/image_raw")

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except CvBridgeError as e:
            rospy.logerr("CvBridge Error: %s", e)
            return
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5,
            minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
        for (x, y, w, h) in faces:
            cv2.rectangle(cv_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(cv_image, 'Face', (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        if len(faces) > 0:
            rospy.loginfo("检测到 %d 张人脸", len(faces))
        cv2.imshow('Face Detection', cv_image)
        cv2.waitKey(1)
        try:
            result_msg = self.bridge.cv2_to_imgmsg(cv_image, 'bgr8')
            result_msg.header = msg.header
            self.image_pub.publish(result_msg)
        except CvBridgeError as e:
            rospy.logerr("发布失败: %s", e)

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    try:
        FaceDetector().run()
    except rospy.ROSInterruptException:
        pass
    finally:
        cv2.destroyAllWindows()
