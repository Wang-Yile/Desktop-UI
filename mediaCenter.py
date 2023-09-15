"""
为 mediaCenter 提供多进程媒体支持
这个库曾经为 tkinter 服务, 因此留下了大量无用的低效代码

upd 2023-08-21 : 删除了视频支持和部分冗余注释
"""

import os
import shutil
import subprocess
import time
import wave

import pyaudio


def sound(path, startT, pause):

    if path[-4:] != ".wav":
        copy_to = os.getenv("temp")+"\\cached-sound."+path.split(sep=".")[-1]
        name = os.getenv("temp")+"\\cached-sound"+str(time.time_ns())+".wav"
        shutil.copyfile(path, copy_to)
        if os.path.exists(name):
            os.remove(name)
        cmd = "powershell.exe; cd '" + os.path.dirname(copy_to) + "'; ffmpeg -i " + os.path.basename(copy_to) + " -vn " + name
        print(cmd)
        subprocess.run(cmd, shell=True)
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
