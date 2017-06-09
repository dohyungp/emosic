import csv
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs

import re
from collections import OrderedDict

with open("link_2501.txt", "r") as f:
    links = [i for i in f.readlines()]
lyrics =[]

for i, link in enumerate(links):
    url = "http://music.naver.com/lyric/index.nhn?trackId={}".format(re.sub(pattern="[^0-9]", repl="", string=link))
    try:
        html = urlopen(url)
        bsObj = bs(html, "html.parser")
        content = bsObj.find("div", {"id": "pop_content"})
        title = content.find("span", {"class": "ico_play"}).get_text().strip()
        artist = content.find("span", {"class": "artist"}).get_text().strip()
        lyric = content.find("div", {"id": "lyricText"}).get_text().strip()
        row = OrderedDict()
        row["title"] = title
        row["artist"] = artist
        row["lyric"] = lyric
        # row = {"idx": i, "title": title, "artist": artist, "lyric": lyric}
        lyrics.append(row)
    except Exception as e:
        print(link, e)

    if i % 100 == 0:
        with open("lyric.csv", "a", newline='', encoding="utf-8") as f:
            fieldnames = row.keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerows(lyrics)
        print("lyric {}".format(i), "success")
        lyrics = []
    elif i == len(links):
        with open("lyric.csv", "a", newline='', encoding="utf-8") as f:
            fieldnames = row.keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(row)
        print("all done")