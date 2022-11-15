from flask import Flask
from flask import render_template
from DatabaseAPI import Database

db = Database()
app = Flask(__name__)

navigation = {
    "Home": "Home"
}


@app.route('/')
@app.route('/home')
def home():  # put application's code here
    # TODO: add auth
    user = "Kenny"
    return render_template("start_page.html", user=user)


@app.route("/all-topics")
def all_topics():
    return render_template("show_all_topics.html")


@app.route("/progress")
def progress():
    return render_template("progress.html")

@app.route('/upload')
def upload():
    return render_template("upload_new_topic.html")

if __name__ == '__main__':
    app.run(debug=True)
