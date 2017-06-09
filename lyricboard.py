import pandas as pd
from flask import Blueprint, render_template, abort
from flask.ext.login import current_user

lyric = Blueprint('lyric', __name__, template_folder='templates')


@lyric.before_request
def check_user():
    if not current_user.is_authenticated:
        abort(403)


@lyric.route("/")
def index():
    return render_template("lyric.html")


@lyric.route("/data")
def get_data():
    df = pd.read_csv("./notebook/LDAcluster.csv").sample(frac=0.01, replace=True)
    df = df[["title", "cluster", "weight", "lyric"]].copy()
    df.columns = ["title", "cluster", "radius", "lyric"]
    return df.to_json(orient='records')
