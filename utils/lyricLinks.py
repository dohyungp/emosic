import csv
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs

links =[]

for i in range(7801, 9849):
    print(i)
    url = "http://music.naver.com/listen/newTrack.nhn?domain=DOMESTIC&target=all&page={}".format(i)

    html = urlopen(url)
    bsObj = bs(html, "html.parser")
    all_links = bsObj.findAll("a", {"class": "_lyric"})
    for link in all_links:
        classpath = link['class']
        if not classpath[1].__eq__('none'):
            start, end = re.search("i:.*", classpath[1]).span()
            links.append(classpath[1][start + 2:end])

    if i % 100 == 0 and len(links) > 0:
        with open('link_7801.txt', 'a') as f:
            for item in links:
                f.write("%s\n" % item)
        print(i, "done")
        links = []
    elif i == 9848:
        with open('link_7801.txt', 'a') as f:
            for item in links:
                f.write("%s\n" % item)
        print(i, "done")
