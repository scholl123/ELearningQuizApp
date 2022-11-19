import os,  openpyxl
import pandas as pd
import random


ALLOWED_EXTENSIONS = ['csv', 'xlsx']
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


diff_translate= {"easy":0, "medium":1, "hard":2}

def transform_input_file_to_topic(path: str,topic : str,file=0 ):
    if ".xlsx" in path:
        pd.read_excel(file).to_csv(r'uploads\ResultCsvFile.csv', index = None, header=True)
        csv_file = pd.read_csv("uploads\ResultCsvFile.csv", encoding="utf-8")
    elif ".csv" in path:
        csv_file = pd.read_csv("uploads\ResultCsvFile.csv", encoding="utf-8")
    df = pd.DataFrame(csv_file)
    output_list= []
    for index, row in df.iterrows():
        question = row["Question"]
        topic = topic
        diff = diff_translate[row["Difficulty"]] if type(row["Difficulty"]) != float else "1"
        if type(row["Alternatives (only for MC)"] )!= float:
            answers = [str(i).strip() for i in row["Alternatives (only for MC)"].split(",")]
            random.shuffle(answers)

            correct_index = random.randint(0,len(answers)-1)
            answers.insert(correct_index, row["Answer"])
        else:
            answers=[row["Answer"]]
            correct_index = 0
        output_list.append({'topic': topic, 'question': question, 'answers': answers, 'correct_index': correct_index, 'difficulty': diff})
    
    return output_list

#transform_input_file_to_topic(path ="test.xlsx", topic ="example")