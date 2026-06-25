#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROS英文语音识别节点：基于pocketsphinx默认英文模型
功能：1. 实时识别麦克风英文语音 2. 终端打印结果 3. 发布到/speech话题
"""
import rospy
from std_msgs.msg import String
from pocketsphinx import LiveSpeech

def speech_recognition_node():
    # 1. 初始化ROS节点
    rospy.init_node('speech_recog_node', anonymous=True)
    # 2. 创建话题发布者
    pub = rospy.Publisher('/speech', String, queue_size=10)
    rospy.loginfo("英文语音识别节点已启动，正在监听语音...")
    
    # 3. 配置Pocketsphinx英文识别（使用默认模型，无需额外文件）
    speech = LiveSpeech(
        verbose=False,       # 关闭详细日志
        sampling_rate=16000, # 采样率
        buffer_size=2048,    # 缓冲区大小
        no_search=False,
        full_utt=False,
        # 仅保留基础配置，使用默认英文模型（无需hmm/lm/dic路径）
    )
    
    # 4. 循环识别语音
    try:
        for phrase in speech:
            recog_result = str(phrase).strip()
            if recog_result:  # 过滤空结果
                # 终端打印（绿色字体突出）
                print(f"\033[32m识别到英文：{recog_result}\033[0m")
                # 发布到ROS话题
                pub.publish(recog_result)
                rospy.loginfo(f"发布结果到/speech：{recog_result}")
    
    except KeyboardInterrupt:
        rospy.loginfo("识别节点已停止")
    except Exception as e:
        rospy.logerr(f"识别出错：{str(e)}")
        print(f"错误详情：{str(e)}")

if __name__ == '__main__':
    try:
        speech_recognition_node()
    except rospy.ROSInterruptException:
        pass
