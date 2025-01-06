import json
import random
from flask import current_app
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

DATABASE_PATH = "database/"

# loaders

def load_visit_count():
    try:
        with open('database/visit_count.json', 'r') as f:
            current_app.logger.info("visit_count.json found and loaded")
            return json.load(f)
    except FileNotFoundError:
        current_app.logger.warning("visit_count.json not found, created and loaded")
        return {'total': 0}
    except Exception as e:
        current_app.logger.error(f"{e}")

def load_question_bank():
    try:
        with open('database/questions_bank.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(e)

def load_comments():
    try:
        with open('database/comments.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"04/01/2025 10:09:20":{
            "Geri":"Hello there!"
        }}
    except Exception as e:
        print(e)

def load_user_status():
    try:
        with open('database/player_login.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(e)

def load_user_creds():
    try:
        with open('database/player_creds.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(e)

def load_history():
    try:
        with open('database/history.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(e)


def load_scores():
    try:
        with open('database/player_rating.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'Bella': 0, 'Herczi': 0, 'Geri': 0, 'Bálint': 0, 'Márk': 0, 'Koppány': 0, 'Hanna': 0}

# savers

def save_player_stat(stat):
    with open('database/player_login.json', 'w') as f:
        json.dump(stat, f)

def save_visit_count(visits):
    with open('database/visit_count.json', 'w') as f:
        json.dump(visits, f)
    
def save_questions(questions):
    with open('database/questions_bank.json', 'w') as f:
        json.dump(questions, f)

def save_scores(values):
    with open('database/player_rating.json', 'w') as f:
        json.dump(values, f)

def save_comments(comments):
    with open('database/comments.json', 'w') as f:
        json.dump(comments, f)

def save_history(history_logs):
    with open('database/history.json', 'w') as f:
        json.dump(history_logs, f)

def get_question():
    questions_bank = load_question_bank()
    questions = {key: value for key, value in questions_bank.items() if value == 0}
    if len(questions) == 0:
        return "----- NO MORE QUESTIONS LEFT -----"
    question = random.choice(list(questions.items()))[0]
    questions_bank[question] = 1
    save_questions(questions_bank)
    return question

def get_daily_question():
    questions_bank = load_question_bank()
    question = {key: value for key, value in questions_bank.items() if value == 1}
    if len(question) == 0:
        return "------ NO MORE QUESTIONS LEFT! ------"
    return list(question.keys())[0]

def daily_routine():
    # save history
    question = get_daily_question()
    scores = load_scores()
    user_comments = load_comments()
    comments_packet = []
    current_date = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    for timestamp, comments in user_comments.items():
        for usern, message in comments.items():
            comments_packet.append({"name": usern, "message": message})

    history_log = {
        "question": question,
        "answers": scores,
        "comments":comments_packet}
    
    history = load_history()
    try:
        history[current_date] = history_log
    except:
        print("History log already exists for this date.")
    save_history(history)

    # RESET

    # reset score
    scores = load_scores() # load
    zero_scores = {key: 0 for key in scores} # change
    save_scores(zero_scores) # save
    print("RESET SCORES")

    # change question
    questions_bank = load_question_bank() # load
    # set yesterday's to be used
    used_questions = {key: value for key, value in questions_bank.items() if value == 2}
    ystd_question = {key: 2 for key, value in questions_bank.items() if value == 1}
    unused_questions = {key: value for key, value in questions_bank.items() if value == 0} # unused
    # select question randomly
    question = random.choice(list(unused_questions.items()))[0]
    # change
    unused_questions[question] = 1 # set for today's Q
    # update
    unused_questions.update(ystd_question)
    unused_questions.update(used_questions)
    save_questions(unused_questions) # save
    print(f"LOG: today Q: {question}")

    stats = load_user_status() # load
    zero_stats = {key: 0 for key in stats} # change
    save_player_stat(zero_stats)# save
    print("RESET USER STATS")

    # reset comments

    comments = {"04/01/2025 10:09:20":{
            "Geri":"First \ud83d\ude01"
        }}
    save_comments(comments) # reset comments


"""
import re

# Original text
text = "Do you think {P} would beat {P} in a drinking game?"

# Names to replace
names = ["Mark", "Herczi"]

# Replace placeholders sequentially
result = re.sub(r"{P}", lambda _: names.pop(0), text)

print(result)
"""