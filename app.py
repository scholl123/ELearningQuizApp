import os
import openpyxl
import pandas as pd
import seaborn as sns
from flask import Flask, render_template, request, redirect, url_for, g
from werkzeug.utils import secure_filename

import file_handling
from DatabaseAPI import Database

import auth

UPLOAD_FOLDER = 'uploads/'

db = Database()
app = Flask(__name__)
app.register_blueprint(auth.auth)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@auth.login_required
@app.route("/", methods=['GET', 'POST'])
def index():
    """root directory of the web interface. Login interface"""
    if g.user is None:
        return redirect(url_for('auth.login'))
    return render_template("quiz_settings.html")


@app.route("/progress")
@auth.login_required
def show_progress():
    uid = g.user['uid']
    user_progress_data = db.get_progress(uid)
    badges = []

    for b in user_progress_data["badges"]:
        count = b["count"] if b["count"] != -1 else 0
        badge_info = db.get_badges(b["bid"])
        obtained = b["count"] == badge_info["target"]
        if badge_info["target"] == -1:
            badge_info["target"] = 1

        badges.append([badge_info, count, obtained])

    data = db.get_user_statistics(uid)
    palette = (sns.color_palette("colorblind", len(data.keys()))).as_hex()
    labels = [i for i in range(0,max(len(x) for x in list(data.values())))]
    data_dict = dict()
    for key in data.keys():
        data_dict["'" +key+"'"] = (data[key], "'"+str(palette.pop())+"'")

    return render_template("progress.html", badge_data=badges, labels=labels, values=data_dict)


@app.route("/show_all_topics")
@auth.login_required
def show_all_topics():
    topics = db.get_topics()
    return render_template("show_all_topics.html", topics=topics)


@app.route("/show_one_topic", methods=['POST'])
@auth.login_required
def show_single_topic():
    if request.method == 'POST':
        difficulty_levels = {0: "easy", 1: "medium", 2: "hard"}
        text = request.form.get("topicId")
        questions = db.get_questions(text)
        for quest in questions:
            quest["difficulty"] = difficulty_levels[quest["difficulty"]]
        return render_template("show_one_topic.html", topic=text, questions=questions)


@app.route("/upload_new_topic")
@auth.login_required
def show_upload_page():
    return render_template("upload_new_topic.html")


@app.route("/uploaded", methods=['POST'])
@auth.login_required
def show_uploaded_page():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        if file and file_handling.allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            x = file_handling.transform_input_file_to_topic(file.filename,
                                                            topic=request.form.get("topic_name"),
                                                            file=file)
            [db.set_question(q) for q in x]
            return render_template("uploaded.html", notice=1)
        else:
            return render_template("uploaded.html", notice=2)
    else:
        return render_template("uploaded.html", notice=0)


@app.route("/result")
@auth.login_required
def show_results():
    values = [(15, 19), (10, 10), (4, 6), (1, 3)]
    return render_template("show_quiz_result.html", result=values)


# test reading form input
@app.route("/quiz", methods=['POST', 'GET'])
@auth.login_required
def quiz():
    if request.method == 'GET':
        return "Something wrong"
    elif request.method == 'POST':
        form_data = request.form
        return render_template("multiple_choice.html", form_data=form_data)


@app.route("/question")
@auth.login_required
def question():
    return render_template("quiz_question.html")

app.secret_key = 'secret example key'

if __name__ == '__main__':
    # flask --app app.py --debug run
    # db_sql.init_app(app)

    app.config['SESSION_TYPE'] = 'filesystem'

    from . import auth

    app.register_blueprint(auth.auth)
    print("hello")
    # session.init_app(app)
    app.run(debug=True)
