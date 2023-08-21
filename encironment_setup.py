# -*- coding=utf-8 -*-

import ctypes
import os
import platform
import sys
import time

CHUNK = 0.01

def getFreeDisk(folder:str) -> int: # 单位: GB

    if platform.system() == "Windows":
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder),
                                                   None, None,
                                                   ctypes.pointer(free_bytes))
        free = free_bytes.value/1024/1024/1024
    elif platform.system() == "Linux":
        st = os.statvfs(folder)
        free =  st.f_bavail * st.f_frsize/1024/1024
    else:
        free = 0
    return free

def rootPath(folder:str) -> str:

    folder = folder.replace("\\", "/")
    if folder[0] == "/":
        return "/" + folder.split(sep="/")[1]
    return folder.split(sep="/")[0] + "/"

def checkEnvironment() -> str:

    res = "[Start Checking Environment]\n"
    if platform.system() in ("Windows", "Darwin", "Linux"):
        res += f"System: {platform.system()} [Accepted]\n"
    else:
        res += f"System: {platform.system()} [Unknown]\n"
    res += f"(Info) System Version: {platform.version()}\n"
    # res += f"{sys.version_info}\n"
    if sys.version_info.major == 3 and sys.version_info.minor >= 10:
        res += f"Python Version: {platform.python_version()} [Accepted]\n"
    else:
        res += f"Python Version: {platform.python_version()} [Unaccepted]\n"
        res += "(Note) Python 3.10 or later Python 3 required\n"
        res += "[Exit 1] Check exited unsuccessfully"
        return res
    root = rootPath(sys.path[4])
    res += f"(Info) Python Installed Path: {root}\n"
    res += f"(Info) Disk Free: {getFreeDisk(root)} GB\n"
    res += "[Exit 0] Check exited successfully\n"
    return res

def setupPackage(package:str):

    os.system(f"python3 -m pip install {package} \
-i http://mirrors.aliyun.com/pypi/simple/ \
--trusted-host mirrors.aliyun.com")

def confirmMessage(msg:str) -> bool:

    msg += " [Y/n]"
    for i in msg:
        print(i, end="")
        time.sleep(CHUNK)
    b = input()
    return b.upper().strip() == "Y"

def tryImportModule(module:str, import_name:str, msg:str=""):

    try:
        __import__(import_name)
        if confirmMessage(f"{module} has already satisfied, check for update now ?"+msg):
            setupPackage(f"{module} --upgrade")
    except (ImportError, ModuleNotFoundError):
        if confirmMessage(f"{module} hasn't satisfied yet, install now ?"+msg):
            setupPackage(module)

def clearStdout():

    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

if __name__ == "__main__":
    for i in range(20):
        print("_Setup Environment_\n"[i], end="")
        time.sleep(CHUNK)
    if not confirmMessage("Setup now ?"):
        sys.exit()
    check_result = checkEnvironment()
    for i in check_result:
        print(i, end="")
        time.sleep(CHUNK)
    if check_result.splitlines()[-1][6] != "0" \
        and not confirmMessage("Environment not satisfied, continue ?"):
        sys.exit()
    tryImportModule("pip", "pip")
    tryImportModule("NumPy", "numpy")
    tryImportModule("Pillow", "PIL")
    tryImportModule("opencv-python", "cv2")
    tryImportModule("pyaudio", "pyaudio")
    tryImportModule("requests", "requests")
    tryImportModule("psutil", "psutil")
    tryImportModule("Pyside6", "PySide6.QtWidgets")
    time.sleep(0.5)
    for i in range(50):
        # os.system("cls")
        clearStdout()
        print("|", end="")
        print("-"*i, end="|\n")
        print("|", end="")
        if i <= 8:
            print("-"*i+"|"+" "*(7-i)+"All modules have already satisfied")
        elif i >= 42:
            print("-"*8+"All modules have already satisfied"+"-"*(i-42)+"|")
        else:
            print("-"*8+"All modules have already satisfied")
        print("|", end="")
        print("-"*i, end="|\n")
        time.sleep(CHUNK)
    for i in range(24):
        print("Now You're ready to go !"[i], end="")
        time.sleep(CHUNK)
