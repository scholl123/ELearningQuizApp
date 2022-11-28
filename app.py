import os

import seaborn as sns
from flask import Flask, render_template, request, redirect, url_for, g, session, flash
from werkzeug.utils import secure_filename

import auth
from utility import get_difficulty_string
import file_handling
from DatabaseAPI import Database

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
    topics = db.get_topics()
    return render_template("quiz_settings.html", topics=topics)


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
    labels = [i for i in range(0, max(len(x) for x in list(data.values())))]
    data_dict = dict()
    for key in data.keys():
        data_dict["'" + key + "'"] = (data[key], "'" + str(palette.pop()) + "'")

    return render_template("progress.html", badge_data=badges, labels=labels, values=data_dict)


@app.route("/topics")
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


@app.route("/quiz", methods=['POST', 'GET'])
@auth.login_required
def quiz_setup():
    session['q_index'] = 0
    session['correct'] = 0

    if request.method == "POST":
        settings = dict()
        settings["topic"] = request.form["topic"]
        settings["num_questions"] = int(request.form["num_questions"])
        settings["difficulty"] = int(request.form["difficulty"])

        session['settings'] = settings

        session['quiz'] = db.get_questions(topic=settings['topic'], diff=settings['difficulty'],
                                           num=settings['num_questions'])

        if len(session['quiz']) == 0:
            flash(f"No more {get_difficulty_string(settings['difficulty'])} questions left.")
            return redirect(url_for("index"))

        session['settings']['num_questions'] = len(session['quiz'])
        return render_template("quiz_question.html", question=session['quiz'][session['q_index']],
                               answered=0)


@app.route("/question", methods=['POST', 'GET'])
@auth.login_required
def question():
    if request.method == 'GET':
        session['q_index'] += 1
        # last question
        if len(session['quiz']) == session['q_index']:
            values = [(session['correct'], len(session['quiz'])), (10, 10), (4, 6), (1, 3)]
            results = session['settings']
            results['correct'] = session['correct']
            db.update_progress(session['user_id'], results)
            return render_template("show_quiz_result.html", result=values)
        return render_template("quiz_question.html", question=session['quiz'][session['q_index']],
                               answered=0)

    elif request.method == 'POST':
        success = True
        answer = request.form.get('answer')
        current_question = session['quiz'][session['q_index']]
        answered = [current_question['answered'][0] + 1, current_question['answered'][1]]
        is_multiple_choice = len(current_question['answers']) > 1
        if is_multiple_choice:
            answer = int(answer)
            if answer == current_question['correct_index']:
                session['correct'] += 1
            else:
                success = False
                answered[1] += 1

        else:  # text-input question
            if answer == current_question['answers'][0]:
                session['correct'] += 1
            else:
                success = False
                answered[1] += 1
        db.set_question({'qid': current_question['qid'], 'answered': answered})
        return render_template("quiz_question.html", question=current_question,
                               show_answer=True, answer=answer, success=success)


app.secret_key = 'secret example key'

if __name__ == '__main__':
    # flask --app app.py --debug run
    # db_sql.init_app(app)

    app.config['SESSION_TYPE'] = 'filesystem'

    import auth

    app.register_blueprint(auth.auth)
    print("hello")
    # session.init_app(app)
    app.run(debug=True)
