import random
import threading
import time

import requests
from PySide6.QtGui import QImage, QPixmap


def getImageFromURL():
    img = QImage()
    while img.isNull():
        index = random.randint(0, 23)
        index2 = random.randint(0, 99)
        string = str(index) + str(index2)
        while len(string) < 4:
            string = "0" + string
        url = "https://cdn.eso.org/images/screen/eso%sa.jpg" % string
        res = requests.get(url)
        img = QImage.fromData(res.content)
    return img

IMAGE_URLS = [
    "eso0934a",
    "eso1625a",
    "eso1250a",
    "eso1208a",
    "eso1119a",
    "eso0925a",
    "eso1723a",
    "eso1031a",
    "eso1031b",
    "eso0650a",
    "eso1006a",
    "eso1422a",
    "eso1233a",
    "potw1119a",
    "eso0926a"
]
IMAGE_CONNECTED = False

def getImageFromURL2():

    global IMAGE_CONNECTED, BACKGROUND_IMAGE
    IMAGE_CONNECTED = False
    if 1 == 1:
        IMAGE_CONNECTED = True
        BACKGROUND_IMAGE = QPixmap("background.jpeg")
        return
    url = random.sample(IMAGE_URLS, 1)[0]
    print("get background image from https://cdn.eso.org/images/screen/%s.jpg" % url)
    url = "https://cdn.eso.org/images/screen/%s.jpg" % url
    t = time.time()
    res = requests.get(url)
    print("connection costs %.3f s" % (time.time()-t))
    BACKGROUND_IMAGE = QPixmap.fromImage(QImage.fromData(res.content))
    IMAGE_CONNECTED = True

IMAGE_THREAD = threading.Thread(target=getImageFromURL2, daemon=True)
# IMAGE_THREAD.start()

BACKGROUND_IMAGE = None
