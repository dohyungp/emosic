import os
from datetime import timedelta

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask.ext.login import LoginManager, login_user, logout_user, current_user
from flask.ext.login import login_required
from flask_paginate import Pagination, get_page_args
from flask_dropzone import Dropzone

from user import User
from dbhelper import DBHelper
from passwordhelper import PasswordHelper

import logging

from dashboard import dashboard
from tagger import tagger
from lyricboard import lyric
from engine import RecommendationEngine

from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession


def init_spark_context():
    conf = SparkConf().setAppName("music_recommendation-server")
    sc = SparkContext(conf=conf, pyFiles=['engine.py', 'emosic.py'])

    return sc


def init_spark_session():
    spark = SparkSession \
        .builder \
        .appName("Recommendation System") \
        .getOrCreate()

    return spark


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB = DBHelper()
PH = PasswordHelper()

app = Flask(__name__)

login_manager = LoginManager(app)
dropzone = Dropzone(app)

app.secret_key = 'tPXJY3X37Qybz4QykV+hOyUxVQeEXf1Ao2C8upz+fGQXKsM'
app.register_blueprint(dashboard, url_prefix='/dashboard')
app.register_blueprint(tagger, url_prefix='/emotion')
app.register_blueprint(lyric, url_prefix='/lyrics')

app.config['UPLOAD_FOLDER'] = os.getcwd() + '/uploads'
app.config.update(
    DROPZONE_ALLOWED_FILE_TYPE='audio',
    DROPZONE_MAX_FILE_SIZE=30,
    DROPZONE_INPUT_NAME='photo',
    DROPZONE_MAX_FILES=1
)


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect("/")


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/recent')
@login_required
def recent():
    total = 100
    page, per_page, offset = get_page_args()
    musics = DB.get_recent(offset, per_page)
    pagination = Pagination(css_framework='bootstrap3', page=page, per_page=per_page, total=total, search=False,
                            record_name='musics', format_total=True, format_number=True,)
    return render_template("recent.html", musics=musics, per_page=per_page, pagination=pagination, page=page,)


@app.route('/top')
@login_required
def top():
    total = 100
    page, per_page, offset = get_page_args()
    musics = DB.get_top(offset, per_page)
    pagination = Pagination(css_framework='bootstrap3', page=page, per_page=per_page, total=total, search=False,
                            record_name='musics', format_total=True, format_number=True,)
    return render_template("top.html", musics=musics, per_page=per_page, pagination=pagination, page=page,)


@login_manager.user_loader
def load_user(user_id):
    user_password = DB.get_user(user_id)
    if user_password:
        return User(user_id)


@app.route("/login_page", methods=["GET"])
def login_page():
    return render_template('login_page.html')


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    stored_user = DB.get_user(email)
    print(stored_user)
    if stored_user and PH.validate_password(password, stored_user[1], stored_user[2]):
        user = User(email=email)
        print("login success")
        login_user(user, remember=True)
        return redirect("/")
    else:
        flash("Error")
    return redirect("/")


@app.route("/register_page", methods=["GET"])
def register_page():
    return render_template('register_page.html')


@app.route("/register", methods=["POST"])
def register():
    email = request.form.get("email")
    name = request.form.get("name")
    pw1 = request.form.get("password")
    pw2 = request.form.get("password_confirm")
    if not pw1 == pw2:
        flash('비밀번호가 틀렸습니다.')
        return redirect(url_for('register_page'))
    if DB.get_user(email):
        return redirect("/")
    salt = PH.get_salt()
    hashed = PH.get_hash(pw1.encode('utf-8') + salt)
    DB.add_user(email, name, salt, hashed)
    return redirect("/")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/music/<int:musicid>")
@login_required
def music(musicid):
    music = DB.get_music(musicid)
    avg_rating = DB.get_avg_rating(musicid)[0]
    personal_rating = DB.get_rating(musicid, current_user.get_id())[0]
    return render_template("music.html", music=music, avg_rating=avg_rating, personal_rating=personal_rating)


@app.route("/rating", methods=["GET", "POST"])
@login_required
def rating():
    musicid, userid, rating = request.form['music'], current_user.get_id(), request.form['rating']
    DB.add_rating(musicid, userid, rating)
    return "thx"


@app.route("/mypage")
@login_required
def mypage():
    user_id = DB.get_user(current_user.get_id())[4]
    logger.debug("User %s TOP ratings requested", user_id)
    count = 20
    top_ratings = recommendation_engine.get_top_ratings(user_id, count)

    return render_template("mypage.html", recommend_list=top_ratings)


if __name__ == '__main__':

    global recommendation_engine

    sc = init_spark_context()
    spark = init_spark_session()
    recommendation_engine = RecommendationEngine(sc, spark)

    app.run()
    sc.stop()
