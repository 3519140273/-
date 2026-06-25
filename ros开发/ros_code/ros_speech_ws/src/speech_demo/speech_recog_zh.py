#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROS语音识别节点：基于pocketsphinx实现中文语音识别
功能：1. 实时识别麦克风语音 2. 终端打印识别结果 3. 发布到/speech话题
"""
import rospy
from std_msgs.msg import String
from pocketsphinx import LiveSpeech
import os

def speech_recognition_node():
    # 1. 初始化ROS节点
    rospy.init_node('speech_recog_node', anonymous=True)
    # 2. 创建话题发布者，发布识别结果到/speech话题
    pub = rospy.Publisher('/speech', String, queue_size=10)
    rospy.loginfo("语音识别节点已启动，正在监听语音...")  # ROS日志打印
    
    # 3. 配置pocketsphinx中文语音识别（需确保已安装中文模型）
    # 若识别英文，可删除以下模型路径配置，使用默认模型
    speech = LiveSpeech(
        verbose=False,
        sampling_rate=16000,
        buffer_size=2048,
        no_search=False,
        full_utt=False,
        # 中文模型路径（需提前安装，下方步骤会说明）
        hmm=os.path.expanduser("~/cmusphinx-zh-cn-5.2/model_parameters/zh-cn/acoustic-model"),
        lm=os.path.expanduser("~/cmusphinx-zh-cn-5.2/model_parameters/zh-cn/language-model.lm.bin"),
        dic=os.path.expanduser("~/cmusphinx-zh-cn-5.2/model_parameters/zh-cn/pronounciation-dictionary.dict")
    )
    
    # 4. 循环识别语音
    try:
        for phrase in speech:
            # 获取识别结果并格式化
            recog_result = str(phrase).strip()
            if recog_result:  # 过滤空识别结果
                # ① 终端打印识别结果（直观查看）
                print(f"\033[32m识别到：{recog_result}\033[0m")  # 绿色字体突出显示
                # ② 发布到ROS /speech话题
                pub.publish(recog_result)
                # ROS日志记录（可选）
                rospy.loginfo(f"发布识别结果到/speech话题：{recog_result}")
    
    except KeyboardInterrupt:
        rospy.loginfo("语音识别节点已停止")
    except Exception as e:
        rospy.logerr(f"识别出错：{str(e)}")
        print(f"错误详情：{str(e)}")

if __name__ == '__main__':
    try:
        speech_recognition_node()
    except rospy.ROSInterruptException:
        pass
