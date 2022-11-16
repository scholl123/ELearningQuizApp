from flask import Flask, render_template, request, session, redirect, url_for
from DatabaseAPI import Database


db = Database()
app = Flask(__name__)


# @app.route('/result',methods = ['POST', 'GET'])
# def result():
#   if request.method == 'POST':
#      result = request.form
#      return render_template("result.multiple_choice.html",result = result)

@app.route("/")
def index():
    return render_template("start_page.html")


@app.route("/quiz_settings")
def show_quiz_settings():
    return render_template("quiz_settings.html")


@app.route("/progress")
def show_progress():
    return render_template("progress.html")


@app.route("/show_all_topics")
def show_all_topics():
    return render_template("show_all_topics.html")


@app.route("/upload_new_topic")
def show_upload_page():
    return render_template("upload_new_topic.html")


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

# @app.route("/quiz")
# def quiz():
#     return render_template("multiple_choice.html")


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


if __name__ == '__main__':
    # flask --app app.py --debug run
    # db_sql.init_app(app)
    app.run(debug=True)
