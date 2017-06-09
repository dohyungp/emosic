import csv
import mysql.connector
from dbconfig import config


cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()
with open("./new_file.csv", "r") as f:
    table = csv.DictReader(f)
    for row in table:
        query = " INSERT INTO rating (musicid, userid, rating) VALUES (%s, %s, %s) "
        cursor.execute(query, (row["musicid"], row["userid"], row["rating"]))

        cnx.commit()

cnx.close()