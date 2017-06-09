import os
from mutagen.mp3 import MP3
import random
import time
from datetime import date
import mysql.connector
from dbconfig import config

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

add_music = (" INSERT INTO music "
             " (genreid, moodid, author, title, length, url, date)"
             " VALUES (%(genre)s, %(mood)s, %(author)s, %(title)s, %(length)s, %(filename)s, %(to_date)s)")

DATASET_DIR = "/home/dobro/project/emosic/media/datasets"
audios = []


def strTimeProp(start, end, format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(format, time.localtime(ptime))


def randomDate(start, end, prop):
    return strTimeProp(start, end, '%m/%d/%Y', prop)


genre_dic = {"Hiphop": 1, "Country": 2, "Jazz": 3, "Pop": 4, "Rock": 5, "Dance": 6, "classic": 7, }
mood_dic = {"Bright": 1, "Happy": 2, "Funky": 3, "Dramatic": 4, "Dark": 5,
            "Calm": 6, "Inspirational": 7, "Angry": 8, "Sad": 9, "Romantic": 10,}
for (path, _, files) in os.walk(DATASET_DIR):
    for filename in files:
        ext = os.path.splitext(filename)[-1]
        title = os.path.splitext(filename)[0]
        if ext == '.mp3':
            fn = os.path.join(path, filename)
            splits = fn.split(os.sep)
            mood = splits[-2]
            genre = splits[-3]
            audio = MP3(fn)
            rdate = randomDate("1/1/2016", "5/18/2017", random.random()).split("/")

            audios.append({"title": title, "filename": os.path.relpath(fn, start="/home/dobro/project/emosic/media"), "length": audio.info.length, "mood": mood_dic[mood], "genre": genre_dic[genre],
                           "author": audio['TPE1'].__str__(), "to_date": date(int(rdate[2]), int(rdate[0]), int(rdate[1]))})


for row in audios:
    print(row)
    cursor.execute(add_music, row)

cnx.commit()
cursor.close()
cnx.close()