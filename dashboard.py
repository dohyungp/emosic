import pandas as pd
import mysql.connector
from flask import Blueprint, render_template, abort
from flask.ext.login import current_user
from dbconfig import config


dashboard = Blueprint('dashboard', __name__, template_folder='templates')


@dashboard.before_request
def check_user():
    if not current_user.is_authenticated:
        abort(403)


@dashboard.route("/")
def index():
    return render_template("dashboard.html")


@dashboard.route("/data")
def get_data():
    cnx = mysql.connector.connect(**config)

    query = "SELECT author, DATE_FORMAT(date, '%m/%d/%Y') as date, g.genre as genre, m2.mood as mood, length as Length " \
            "FROM music m1, genre g, mood m2 WHERE m1.genreid = g.genreid and m2.moodid = m1.moodid"

    df = pd.read_sql(query, cnx)
    return df.to_json(orient='records')
