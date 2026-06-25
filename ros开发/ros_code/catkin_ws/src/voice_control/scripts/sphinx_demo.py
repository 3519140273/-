#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PocketSphinx 离线语音识别"""

import rospy
from std_msgs.msg import String
import speech_recognition as sr

class SphinxDemo:
    def __init__(self):
        rospy.init_node("sphinx_demo", anonymous=True)
        self.pub = rospy.Publisher("/voice/recognized", String, queue_size=10)
        self.rec = sr.Recognizer()
        self.mic = sr.Microphone()
        rospy.loginfo("PocketSphinx 已启动!")

    def recognize(self):
        with self.mic as source:
            self.rec.adjust_for_ambient_noise(source, duration=1)
            rospy.loginfo("[Sphinx] 请说话...")
            try:
                audio = self.rec.listen(source, timeout=5, phrase_time_limit=3)
            except sr.WaitTimeoutError:
                rospy.loginfo("[Sphinx] 超时")
                return ""
        try:
            text = self.rec.recognize_sphinx(audio)
            rospy.loginfo("[Sphinx] 识别: %s", text)
            return text
        except sr.UnknownValueError:
            rospy.loginfo("[Sphinx] 无法识别")
            return ""
        except sr.RequestError as e:
            rospy.logerr("[Sphinx] 错误: %s", e)
            return ""

    def run(self):
        while not rospy.is_shutdown():
            rospy.loginfo("\n[提示] 按 Enter 识别 (q 退出)")
            if input().strip().lower() == 'q':
                break
            text = self.recognize()
            if text:
                self.pub.publish(String(data=text))

if __name__ == "__main__":
    try:
        SphinxDemo().run()
    except rospy.ROSInterruptException:
        pass
