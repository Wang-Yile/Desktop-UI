import json

import requests

HEADERS = { # 浏览器 F12 控制台 alert(navigator.userAgent)
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.31"
}
TIMEOUT = 3
MAX_WORM = 10

def worm_api():

    with open("worm_output/find", "w", encoding="utf-8") as file:
        lst = []
        index = 1
        while index < MAX_WORM:
            # https://flk.npc.gov.cn/api/?page=2&type=flfg&searchType=title%3Bvague&sortTr=f_bbrq_s%3Bdesc&gbrqStart=&gbrqEnd=&sxrqStart=&sxrqEnd=&sort=true&size=10
            result = requests.get(url=r"https://flk.npc.gov.cn/api/?page=" + str(index) + r"&type=flfg&searchType=title%3Bvague&sortTr=f_bbrq_s%3Bdesc&gbrqStart=&gbrqEnd=&sxrqStart=&sxrqEnd=&sort=true&size=10", headers=HEADERS)
            # file.write(result.text)
            content = json.loads(result.text)
            if content["success"] == False:
                continue
            for i in content["result"]["data"]:
                lst.append([i["title"], i["office"], i["publish"], i["expiry"], i["type"]])
            index += 1
        for i in lst:
            file.write(i[0])
            file.write("\n")
            for j in range(1, len(i)):
                file.write("  ")
                file.write(i[j])
                file.write("\n")
    with open("worm_output/find.json", "w", encoding="utf-8") as file:
        json.dump(lst, file, indent="  ", ensure_ascii=False)

worm_api()
