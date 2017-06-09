import os
import shutil

import tensorflow as tf
from flask import Blueprint, render_template, abort, request
from flask import current_app as app
from flask.ext.login import current_user
from werkzeug.utils import secure_filename

from model import cnn
from genre_model import cnn as genre_cnn
from utils.preprocessing import log_ceps

tagger = Blueprint('tagger', __name__, template_folder='templates')

ALLOWED_EXTENSIONS = set(['mp3', 'wav', 'au'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


TYPES = ['밝은', '행복한', '펑키한', '격정적인', '어두운',
         '조용한', '영감을 주는', '화난', '슬픈', '로맨틱한']

GENRE = ['힙합', '컨트리', '재즈', '팝', '락', '댄스', '클래식']

x = tf.placeholder("float", [None, 96, 1366, 1])
sess = tf.Session()
phase_train = tf.placeholder(tf.bool, name='phase_train')

with tf.variable_scope("convolutional"):
    y1, variables = cnn(x, phase_train)
    sess.run(tf.global_variables_initializer())
    saver = tf.train.Saver(variables)
    saver.restore(sess, "emosic_model/mood/model.ckpt")

with tf.variable_scope("genre_convolutional"):
    y2, variables = genre_cnn(x, phase_train)
    sess.run(tf.global_variables_initializer())
    saver = tf.train.Saver(variables)
    saver.restore(sess, "emosic_model/genre/model.ckpt")


def convolutional(input):
    return sess.run(y1, feed_dict={x: input, phase_train: True}).flatten().tolist()


def genre_convolutional(input):
    return sess.run(y2, feed_dict={x: input, phase_train: True}).flatten().tolist()


def transform(fn):
    mel = log_ceps(fn).reshape(-1, 96, 1366, 1)
    print(mel)
    mresults = []
    gresults = []
    mood_results = convolutional(mel)
    genre_results = genre_convolutional(mel)
    for i, e in enumerate(mood_results):
        mresults.append({'type': TYPES[i], 'weight': e})
    print(mresults)
    for i, e in enumerate(genre_results):
        gresults.append({'type': GENRE[i], 'weight': e})
    print(gresults)
    return mresults, gresults


@tagger.before_request
def check_user():
    if not current_user.is_authenticated:
        abort(403)


@tagger.route("/", methods=['GET', 'POST'])
def emotion():
    return render_template('emotion.html')


@tagger.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            saveDir = os.path.join(app.config['UPLOAD_FOLDER'], current_user.get_id())
            os.mkdir(saveDir)
            filename = secure_filename(file.filename)
            ext = os.path.splitext(filename)[-1]
            fn = os.path.join(saveDir, "tmp" + ext)
            file.save(fn)
            print("DONE")
    return "DONE"


@tagger.route("/complete")
def complete():
    mresults = None
    gresults = None
    tmp_dir = os.path.join(app.config['UPLOAD_FOLDER'], current_user.get_id())
    fn = os.path.join(tmp_dir, os.listdir(tmp_dir)[0])
    try:
        mresults, gresults = transform(fn)
    except Exception as e:
        print(e)
    finally:
        shutil.rmtree(tmp_dir)
    return render_template("emotion.html", mresults=mresults, gresults=gresults)
