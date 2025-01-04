import json
import random

def load_visit_count():
    try:
        with open('visit_count.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(e)

def save_visit_count(visits):
    with open('visit_count.json', 'w') as f:
        json.dump(visits, f)

def load_question():
    try:
        with open('questions_bank.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(e)
    
def save_questions(questions):
    with open('questions_bank.json', 'w') as f:
        json.dump(questions, f)

def load_user_status():
    try:
        with open('player_login.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(e)

def load_user_creds():
    try:
        with open('player_creds.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(e)


def save_player_stat(stat):
    with open('player_login.json', 'w') as f:
        json.dump(stat, f)

def get_question():
    questions_bank = load_question()
    questions = {key: value for key, value in questions_bank.items() if value == 0}
    if len(questions) == 0:
        return "----- NO MORE QUESTIONS LEFT -----"
    question = random.choice(list(questions.items()))[0]
    questions_bank[question] = 1
    save_questions(questions_bank)
    return question

def get_daily_question():
    questions_bank = load_question()
    question = {key: value for key, value in questions_bank.items() if value == 1}
    if len(question) == 0:
        return "------ NO MORE QUESTIONS LEFT! ------"
    return list(question.keys())[0]

def load_scores():
    try:
        with open('player_rating.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'Bella': 0, 'Herczi': 0, 'Geri': 0, 'Bálint': 0, 'Márk': 0, 'Koppány': 0, 'Hanna': 0}

def save_scores(values):
    with open('player_rating.json', 'w') as f:
        json.dump(values, f)

def daily_reset():
    # reset score
    scores = load_scores() # load
    zero_scores = {key: 0 for key in scores} # change
    save_scores(zero_scores) # save
    print("RESET SCORES")

    # change question
    questions_bank = load_question() # load
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
    print("RESET STATS")

