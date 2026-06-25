#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""语音控制小海龟 -- 科大讯飞语音听写 (HMAC-SHA256鉴权)"""

import rospy
from geometry_msgs.msg import Twist

import json, base64, hashlib, hmac, time, threading
from datetime import datetime
from urllib.parse import urlencode, quote
import pyaudio, websocket

APP_ID      = "67a228fa"
API_KEY     = "49e72373186a15a8cf5161efaf8c91ba"
API_SECRET  = "MGFkODEzNTNhOTIxNzNjNjdjNGY0MDFj"

HOST         = "iat-api.xfyun.cn"
SAMPLE_RATE  = 16000
CHUNK        = 3200
LINEAR_SPEED = 1.0
ANGULAR_SPEED = 1.0


class IFlytekASR:
    def __init__(self, app_id, api_key, api_secret):
        self.app_id, self.api_key = app_id, api_key
        self.api_secret = api_secret
        self.result_text = ""
        self.running = True
        self.connected = threading.Event()

    def _build_url(self):
        now = datetime.utcnow()
        date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")
        sig_raw = "host: {}\ndate: {}\nGET /v2/iat HTTP/1.1".format(HOST, date)
        sig = base64.b64encode(hmac.new(
            self.api_secret.encode(), sig_raw.encode(), hashlib.sha256
        ).digest()).decode()
        auth_raw = 'api_key="{}", algorithm="hmac-sha256", headers="host date request-line", signature="{}"'.format(
            self.api_key, sig)
        auth = base64.b64encode(auth_raw.encode()).decode()
        return "wss://{}/v2/iat?authorization={}&date={}&host={}".format(
            HOST, quote(auth), quote(date), HOST)

    def _on_open(self, ws):
        # 先发参数帧，再通知音频线程开始
        params = {
            "common":  {"app_id": self.app_id},
            "business": {"language":"zh_cn","domain":"iat","accent":"mandarin","vad_eos":3000,"dwa":"wpgs"},
            "data":    {"status":0,"format":"audio/L16;rate=16000","encoding":"raw","audio":""}
        }
        ws.send(json.dumps(params))
        self.connected.set()
        rospy.loginfo("[讯飞] 已连接，请说话...")

    def _on_message(self, ws, message):
        data = json.loads(message)
        code = data.get("code", 0)
        if code != 0:
            rospy.logerr("[讯飞] 错误: %s", data.get("message",""))
            return
        if "data" in data and "result" in data["data"]:
            parts = []
            for item in data["data"]["result"].get("ws",[]):
                for w in item.get("cw",[]):
                    if w.get("w"): parts.append(w["w"])
            text = "".join(parts)
            if text:
                if data["data"].get("status",0) == 1:
                    rospy.loginfo("[讯飞] 最终: %s", text)
                    self.result_text = text
                    ws.close()
                else:
                    rospy.loginfo("[讯飞] 中间: %s", text)

    def _on_error(self, ws, error):
        rospy.logerr("[讯飞] 错误: %s", error)

    def _on_close(self, ws, code, msg):
        rospy.loginfo("[讯飞] 已断开")
        self.running = False

    def _send_audio(self, ws):
        # 等待连接就绪 + 参数帧发送完成
        self.connected.wait()
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE,
                        input=True, frames_per_buffer=CHUNK)
        rospy.loginfo("[讯飞] 录音中...")
        while self.running:
            try:
                chunk = stream.read(CHUNK, exception_on_overflow=False)
                # base64 编码后放入 JSON 文本帧
                frame = {"data":{"status":1,"format":"audio/L16;rate=16000","encoding":"raw","audio":base64.b64encode(chunk).decode()}}
                ws.send(json.dumps(frame))
            except:
                break
        # 结束帧
        end = {"data":{"status":2,"format":"audio/L16;rate=16000","encoding":"raw","audio":""}}
        try:
            ws.send(json.dumps(end))
        except:
            pass
        stream.stop_stream(); stream.close(); p.terminate()

    def recognize_once(self, timeout=15):
        self.result_text = ""; self.running = True; self.connected.clear()
        ws = websocket.WebSocketApp(self._build_url(),
            on_open=self._on_open, on_message=self._on_message,
            on_error=self._on_error, on_close=self._on_close)
        t = threading.Thread(target=self._send_audio, args=(ws,)); t.daemon = True
        t.start(); ws.run_forever(); t.join(timeout=2)
        return self.result_text


class VoiceControlNode:
    def __init__(self):
        rospy.init_node("voice_control_node", anonymous=True)
        self.cmd_pub = rospy.Publisher("/turtle1/cmd_vel", Twist, queue_size=10)
        self.asr = IFlytekASR(APP_ID, API_KEY, API_SECRET)
        rospy.loginfo("="*50)
        rospy.loginfo("  语音控制小海龟已启动!")
        rospy.loginfo("  命令: 前进/后退/左转/右转/停止")
        rospy.loginfo("="*50)

    def parse(self, text):
        if not text: return None
        t = text.strip()
        if any(w in t for w in ["前进","往前走","向前","直走"]): return "forward"
        if any(w in t for w in ["后退","往后走","向后","倒退"]): return "backward"
        if any(w in t for w in ["左转","向左转","往左转"]): return "left"
        if any(w in t for w in ["右转","向右转","往右转"]): return "right"
        if any(w in t for w in ["停止","停","停下","别动"]): return "stop"
        return None

    def execute(self, cmd):
        t = Twist()
        nm = ""
        if cmd == "forward":   t.linear.x = LINEAR_SPEED; nm = "前进"
        elif cmd == "backward": t.linear.x = -LINEAR_SPEED; nm = "后退"
        elif cmd == "left":     t.angular.z = ANGULAR_SPEED; nm = "左转"
        elif cmd == "right":    t.angular.z = -ANGULAR_SPEED; nm = "右转"
        elif cmd == "stop":     nm = "停止"
        self.cmd_pub.publish(t)
        rospy.loginfo("[控制] %s", nm)

    def run(self):
        while not rospy.is_shutdown():
            rospy.loginfo("\n[提示] 按 Enter 开始 (q 退出)")
            inp = input().strip()
            if inp.lower() == 'q': break
            txt = self.asr.recognize_once()
            if txt:
                cmd = self.parse(txt)
                if cmd:
                    self.execute(cmd)
                    rospy.sleep(1.0)
                    self.execute("stop")
                else:
                    rospy.loginfo("未知命令: %s", txt)
            else:
                rospy.loginfo("未识别")

if __name__ == "__main__":
    try:
        VoiceControlNode().run()
    except rospy.ROSInterruptException:
        pass
