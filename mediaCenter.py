"""
下一步: 使用 taichi 加速 resize 操作
"""

import os
import shutil
import subprocess
import time
import wave
from multiprocessing import Process, Queue, Value
from tkinter import *

import cv2
import pyaudio
from PIL import Image


def read(from_, queue, width, height, fps, start, startT):

    video = cv2.VideoCapture(from_)
    fps.value = video.get(5)
    ret = True
    def resizeIMGW(owidth, oheight, awidth):
        return (int(awidth), int(oheight/owidth*awidth))
    def resizeIMGH(owidth, oheight, aheight):
        return (int(owidth/oheight*aheight), int(aheight))
    while not start.value:
        time.sleep(0.01)
    startT.value = time.time()
    while True:
        if queue.qsize() > fps.value:
            continue
        ret, frame = video.read()
        if not ret:
            video = cv2.VideoCapture(from_)
            ret = True
            continue
        # https://blog.csdn.net/byron123456sfsfsfa/article/details/102996399
        w = resizeIMGW(len(frame[0]), len(frame), width.value)
        if w[0] <= width.value and w[1] <= height.value:
            aw, ah = w
        else:
            aw, ah = resizeIMGH(len(frame[0]), len(frame), height.value)
        if aw > len(frame) or ah > len(frame):
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (aw, ah), interpolation=cv2.INTER_LANCZOS4)
            frame = Image.fromarray(frame)
        else:
            frame = cv2.resize(frame, (aw, ah), interpolation=cv2.INTER_LANCZOS4)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
        queue.put(frame)

def read2(from_, queue, fps, start, startT):

    video = cv2.VideoCapture(from_)
    fps.value = video.get(5)
    ret = True
    while not start.value:
        time.sleep(0.01)
    startT.value = time.time()
    while True:
        if queue.qsize() > fps.value:
            continue
        ret, frame = video.read()
        if not ret:
            video = cv2.VideoCapture(from_)
            ret = True
            continue
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)
        queue.put(frame)

def read2(from_, queue, fps, start, startT):

    video = cv2.VideoCapture(from_)
    fps.value = video.get(5)
    ret = True
    while not start.value:
        time.sleep(0.01)
    startT.value = time.time()
    while True:
        if queue.qsize() > fps.value:
            continue
        ret, frame = video.read()
        if not ret:
            video = cv2.VideoCapture(from_)
            ret = True
            continue
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)
        queue.put(frame)

def sound(path, startT, pause):

    if path[-4:] != ".wav":
        # hs = hash(path)
        # shutil.copyfile(path, os.getenv("temp")+"\\cached-sound%d."%(hs)+path.split(sep=".")[-1])
        # tmp = os.getenv("temp")+"\\cached-sound%d."%(hs)+path.split(sep=".")[-1]
        # if os.path.exists(os.getenv("temp")+"\\cached-sound%d.wav"%(hs)):
        #     os.remove(os.getenv("temp")+"\\cached-sound%d.wav"%(hs))
        # subprocess.run("powershell.exe; cd '" + os.path.dirname(tmp) + "'; ffmpeg -i " + os.path.basename(tmp) + " " + os.getenv("temp") + "\\cached-sound%d.wav"%(hs), shell=True)
        # if os.path.exists(os.getenv("temp")+"\\cached-sound%d.wav")%(hs):
        #     path = os.getenv("temp")+"\\cached-sound%d.wav"%(hs)
        # else:
        #     return 0
        copy_to = os.getenv("temp")+"\\cached-sound."+path.split(sep=".")[-1]
        name = os.getenv("temp")+"\\cached-sound"+str(time.time_ns())+".wav"
        shutil.copyfile(path, copy_to)
        if os.path.exists(name):
            os.remove(name)
        subprocess.run("powershell.exe; cd '" + os.path.dirname(copy_to) + "'; ffmpeg -i " + os.path.basename(copy_to) + " " + name, shell=True)
        if os.path.exists(name):
            path = name
        else:
            startT.value = time.time()
            return 0
    ofile = wave.open(path, "rb")
    p = pyaudio.PyAudio()
    stream = p.open(
        format=p.get_format_from_width(ofile.getsampwidth()),
        channels=ofile.getnchannels(),
        rate=ofile.getframerate(),
        output=True
    )
    startT.value = time.time()
    while True:
        file = wave.open(path, "rb")
        data = file.readframes(1024)
        while data != b"":
            while pause.value:
                time.sleep(0.01)
            stream.write(data)
            data = file.readframes(1024)

if __name__ == "__main__":
    path = "C:\\Users\\bluew\\Desktop\\bilibili\\rick.mp4"
    spath = "C:\\Users\\bluew\\Desktop\\bilibili\\rick.mp3"
    videoQ = Queue()
    widthV = Value("d", 100)
    heightV = Value("d", 100)
    fpsV = Value("d", 0)
    startV = Value("b", False)
    pauseV = Value("b", False)
    readP = Process(target=read, args=(path, videoQ, widthV, heightV, fpsV, startV))
    readP.daemon = True
    soundP = Process(target=sound, args=(spath, startV, pauseV))
    soundP.daemon = True
    readP.start()
    soundP.start()
    print("---end---")