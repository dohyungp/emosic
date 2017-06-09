import mysql.connector
from dbconfig import config


class DBHelper:

    def connect(self, config=config):
        return mysql.connector.connect(**config)

    def add_user(self, *row):
        cnx = self.connect()
        cursor = cnx.cursor()
        try:
            query = ("INSERT INTO user (email, name, salt, hashed) VALUES(%s, %s, %s, %s) ")
            cursor.execute(query, row)
            cnx.commit()
        except Exception as e:
            print(e)
        finally:
            cnx.close()

    def get_user(self, email):
        cnx = self.connect()
        cursor = cnx.cursor()
        user = None
        try:
            query = """SELECT email, salt, hashed, name, userid FROM user WHERE email = %s"""
            cursor.execute(query, (email.strip(), ))

            user = cursor.fetchone()
        except Exception as e:
            print(e)
        finally:
            cnx.close()
        return user

    def get_recent(self, start, end):
        cnx = self.connect()
        cursor = cnx.cursor(dictionary=True)
        musics = None
        try:
            query = " SELECT musicid, title, author, g.genre as genre, url, cover, date " \
                    "FROM music m INNER JOIN genre g ON m.genreid = g.genreid ORDER BY date DESC limit %s, %s"
            cursor.execute(query, (start, end))

            musics = cursor.fetchall()
        except Exception as e:
            print(e)
        finally:
            cnx.close()
        return musics

    def get_top(self, start, end):
        cnx = self.connect()
        cursor = cnx.cursor(dictionary=True)
        musics = None
        try:
            query = "SELECT m.musicid musicid, m.title title, author author, g.genre genre, url, cover, T2.avg_rating avg_rating " \
                    "FROM music m, genre g, " \
                    "(SELECT musicid, avg_rating " \
                    "FROM (SELECT musicid,  AVG(rating) as avg_rating " \
                    "FROM rating GROUP BY musicid) as T " \
                    "ORDER BY avg_rating DESC limit %s, %s) as T2 " \
                    "WHERE m.musicid = T2.musicid and m.genreid = g.genreid;"
            cursor.execute(query, (start, end))

            musics = cursor.fetchall()
        except Exception as e:
            print(e)
        finally:
            cnx.close()
        return musics

    def get_music(self, musicid):
        cnx = self.connect()
        cursor = cnx.cursor(dictionary=True)
        music = None
        try:
            query = " SELECT musicid, title, author, g.genre as genre, url, cover " \
                    "FROM music m INNER JOIN genre g ON m.genreid = g.genreid WHERE m.musicid = %s"
            cursor.execute(query, (musicid, ))

            music = cursor.fetchone()
        except Exception as e:
            print(e)
        finally:
            cnx.close()
        return music

    def add_rating(self, musicid, email, rating):
        cnx = self.connect()
        cursor = cnx.cursor(dictionary=True)
        try:
            query = "INSERT INTO rating (musicid, userid, rating) " \
                    "VALUES (%(music)s, ( SELECT u.userid FROM user u WHERE u.email = %(email)s ), %(rating)s) " \
                    "ON DUPLICATE KEY UPDATE rating=%(rating)s, timestamp=CURRENT_TIMESTAMP();"
            condition = {
                "music": musicid,
                "email": email,
                "rating": rating,
            }
            cursor.execute(query, condition)
            cnx.commit()
        except Exception as e:
            print(e)
        finally:
            cnx.close()

    def get_avg_rating(self, musicid):
        cnx = self.connect()
        cursor = cnx.cursor()
        rating = (0, )
        try:
            query = " SELECT AVG(rating) as avg_rating " \
                    "FROM rating WHERE musicid = %s"
            cursor.execute(query, (musicid, ))

            rating = cursor.fetchone()
            if rating is None:
                rating = (0, )
        except Exception as e:
            print(e)
        finally:
            cnx.close()
        return rating

    def get_rating(self, musicid, userid):
        cnx = self.connect()
        cursor = cnx.cursor()
        rating = (0, )
        try:
            query = " SELECT rating " \
                    "FROM rating WHERE musicid = %s and userid = (SELECT userid FROM user WHERE email = %s)"
            cursor.execute(query, (musicid, userid))

            rating = cursor.fetchone()
            print(rating)
            if rating is None:
                rating = (0, )
        except Exception as e:
            print(e)
        finally:
            cnx.close()
        return rating

