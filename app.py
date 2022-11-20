from flask import Flask, render_template, request, session, redirect, url_for, flash
from DatabaseAPI import Database
from werkzeug.utils import secure_filename
from hashlib import md5
import os
import openpyxl
import pandas as pd
import file_handling

UPLOAD_FOLDER = 'uploads/'


db = Database()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

uid = None
user = None

# @app.route('/result',methods = ['POST', 'GET'])
# def result():
#   if request.method == 'POST':
#      result = request.form
#      return render_template("result.multiple_choice.html",result = result)


@app.route("/", methods=['GET', 'POST'])
def index():
    """root directory of the web interface. Login interface"""
    global uid
    global user
    # when credentials are submitted
    if request.method == 'POST':
        # get input from entry fields
        name = request.form['name']
        password = request.form['password']
        # check for if admin logged in
        doc = db.get_user(name, password)
        if doc is not None:
            uid = doc['uid']
            user = f'{doc["fname"]} {doc["lname"]}'
            return render_template("quiz_settings.html", user=user)
        # login/password not found, return error message
        return render_template('login.html', error=1)
    elif uid is not None:
        return render_template("quiz_settings.html", user=user)
    # initial call
    else:
        return render_template('login.html')


@app.route("/progress")
def show_progress():
    user_progress_data = db.get_progress(1)
    badges = []  
    for b in user_progress_data["badges"]:
        count = b["count"] if b["count"] != -1 else 0
        badge_info = db.get_badges(b["bid"])
        obtained = b["count"] == badge_info["target"]
        if badge_info["target"] == -1:
            badge_info["target"] = 1
            
        badges.append([badge_info, count, obtained])
    del user_progress_data["uid"]
    del user_progress_data["badges"]
    return render_template("progress.html", progress_data=user_progress_data, badge_data=badges)


@app.route("/show_all_topics")
def show_all_topics():
    topics = db.get_topics()
    return render_template("show_all_topics.html", topics=topics)


@app.route("/show_one_topic", methods=['POST'])
def show_single_topic():
    if request.method == 'POST':
        difficulty_levels = {0: "easy", 1: "medium", 2: "hard"}
        text = request.form.get("topicId")
        questions = db.get_questions(text)
        for quest in questions:
            quest["difficulty"] = difficulty_levels[quest["difficulty"]]
        return render_template("show_one_topic.html", topic=text, questions=questions)


@app.route("/upload_new_topic")
def show_upload_page():
    return render_template("upload_new_topic.html")


@app.route("/uploaded", methods=['POST'])
def show_uploaded_page():

    if request.method == 'POST':
        file = request.files['the_file']
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
def show_results():
    values = [(15, 19), (10, 10), (4, 6), (1, 3)]
    return render_template("show_quiz_result.html", result=values)


# test reading form input
@app.route("/quiz", methods=['POST', 'GET'])
def quiz():
    if request.method == 'GET':
        return "Something wrong"
    elif request.method == 'POST':
        form_data = request.form
        print(form_data.to_dict())
        return render_template("multiple_choice.html", form_data=form_data)


@app.route("/question")
def question():
    return render_template("quiz_question.html")


@app.route("/testing", methods=['POST', 'GET'])
def testing():
    if request.method == 'POST':
        return redirect(url_for("quiz"))
    else:
        form_data = request.form
        return "GET"


def is_valid_login(username, password):
    with app.test_request_context('/hello', method='POST'):
        # now you can do something with the request until the
        # end of the with block, such as basic assertions:
        assert request.path == '/hello'
        assert request.method == 'POST'
    pass


app.secret_key = 'secret example key'
if __name__ == '__main__':
    # flask --app app.py --debug run
    # db_sql.init_app(app)

    app.config['SESSION_TYPE'] = 'filesystem'

    # session.init_app(app)
    app.run(debug=True)
