from flask import Flask, render_template, request
app = Flask(__name__)


#@app.route('/result',methods = ['POST', 'GET'])
#def result():
#   if request.method == 'POST':
#      result = request.form
#      return render_template("result.html",result = result) 

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
   values = [(15,19),(10,10),(4,6), (1,3)]
   return render_template("show_quiz_result.html", result= values)

if __name__ == '__main__':
   app.run(debug = True)