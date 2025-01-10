import json
import random
from flask import current_app
from datetime import datetime, timedelta
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
    except FileNotFoundError:
        return {
            "Q1": {
                "Type": 0,
                "Q": "Most likely to give the best advice for a friend in bad mood?",
                "A": {
                    "Bálint":0,
                    "Bella":0,
                    "Geri":0,
                    "Herczi":0,
                    "Hanna":0,
                    "Koppány":0,
                    "Márk":0
                },
                "Status": 0
                }
        }
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

def load_user_db():
    try:
        with open('database/user_db.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(e)

def load_user_votes():
    """
    return {UID:{ name:NAME,voted:01 },...}
    """
    user_db = load_user_db()
    user_votes = {}
    for key, value in user_db.items():
        user_votes[key] = {}
        user_votes[key]["name"] = value["name"]
        user_votes[key]["voted"] = value["voted"]
    return user_votes

def load_user_login():
    """
    return {UID:{ name:NAME:loggedin:01 },...}
    """
    user_db = load_user_db()
    user_login = {}
    for key, value in user_db.items():
        user_login[key] = {}
        user_login[key]["name"] = value["name"]
        user_login[key]["loggedin"] = value["loggedin"]
    return user_login

def load_user_streak():
    """
    return {UID:{ name:NAME,streak:4 },...}
    """
    user_db = load_user_db()
    user_streak = {}
    for key, value in user_db.items():
        user_streak[key] = {}
        user_streak[key]["name"] = value["name"]
        user_streak[key]["streak"] = value["streak"]
    return user_streak

def load_user_creds():
    user_db = load_user_db()
    user_creds = {value["name"]:value["passw"] for key, value in user_db.items()}
    return user_creds

def load_today_poll():
    try:
        with open('database/today_poll.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "Q1": {
                "Type": 0,
                "Question": "Most likely to give the best advice for a friend in bad mood?",
                "Answers": {
                    "Bálint":0,
                    "Bella":0,
                    "Geri":0,
                    "Herczi":0,
                    "Hanna":0,
                    "Koppány":0,
                    "Márk":0
                },
                "Status": 1
                }
        }

def load_history():
    try:
        with open('database/history.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(e)

# savers

def save_user_db(user_db):
    with open('database/user_db.json', 'w') as f:
        json.dump(user_db, f)

def save_users_vote(stat):
    user_db = load_user_db()
    user_db_copy = {}
    for uid, details in user_db.items():
        for id, name_voted in stat.items():
            if details["name"] == name_voted['name']:
                details_copy = details
                details_copy["voted"] = name_voted['voted']
                user_db_copy[uid] = details_copy
    
    save_user_db(user_db_copy)

def save_users_login(login):
    user_db = load_user_db()
    user_db_copy = {}
    for uid, details in user_db.items():
        for id, name_login in login.items():
            if details["name"] == name_login["name"]:
                details_copy = details
                details_copy["loggedin"] = name_login["loggedin"]
                user_db_copy[uid] = details_copy
    
    save_user_db(user_db_copy)

def save_users_streak(streak):
    user_db = load_user_db()
    user_db_copy = {}
    for uid, details in user_db.items():
        for id, name_login in streak.items():
            if details["name"] == name_login["name"]:
                details_copy = details
                details_copy["streak"] = name_login["streak"]
                user_db_copy[uid] = details_copy
    
    save_user_db(user_db_copy)

def save_visit_count(visits):
    with open('database/visit_count.json', 'w') as f:
        json.dump(visits, f)
    
def save_questions(questions):
    with open('database/questions_bank.json', 'w') as f:
        json.dump(questions, f, indent=4)

def save_daily_poll(daily_poll):
    with open('database/today_poll.json', 'w') as f:
        json.dump(daily_poll, f)

def save_comments(comments):
    with open('database/comments.json', 'w') as f:
        json.dump(comments, f)

def save_history(history_logs):
    with open('database/history.json', 'w') as f:
        json.dump(history_logs, f)

def save_new_question(qid,q):
    questions_bank = load_question_bank()
    questions_bank[qid] = q
    with open('database/questions_bank.json', 'w') as f:
        json.dump(questions_bank, f, indent=4)

# getters

def get_new_question_id():
    questions = load_question_bank()
    return len(questions)+1

def get_daily_question():
    try:
        with open('database/today_poll.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(e)

def get_vote_count():
    user_votes = load_user_votes()
    vote_count = 0
    for details in user_votes.values():
        vote_count += details["voted"]
    if vote_count >= 0 and vote_count <= 7: # user count hardcoded
        return vote_count

def get_user_names():
    users = load_user_login()
    usernames = []
    for value in users.values():
        usernames.append(value["name"])
    return usernames

def get_daily_results():
    daily_poll = get_daily_question()
    results = list(daily_poll["Answers"].values())
    return results

def get_comments_packet():
    user_comments = load_comments()
    comments_packet = []
    for comments in user_comments.values():
        for usern, message in comments.items():
            comments_packet.append({"name": usern, "message": message})
    return comments_packet


def set_daily_question():
    questions_bank = load_question_bank()
    question = {}
    for qid, details in questions_bank.items():
        if details["Status"] == 1:
            for k,v in details.items():
                question[k] = v
    with open('database/today_poll.json', 'w') as f:
        json.dump(question, f)

def daily_routine():

    #BACKUP

    # save history
    question = get_daily_question()
    user_comments = load_comments()
    user_votes = load_user_votes()
    comments_packet = []
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_date = yesterday.strftime("%d-%m-%Y")
    for timestamp, comments in user_comments.items():
        for usern, message in comments.items():
            comments_packet.append({"name": usern, "message": message})

    history_log = {
        "Type": question["Type"],
        "Question": question["Question"],
        "Answers": question["Answers"],
        "Voted": user_votes,
        "Comments": comments_packet
        }
    
    history = load_history()
    
    try:
        history[yesterday_date] = history_log
    except:
        print("History log already exists for this date.")
    
    save_history(history)

    # RESET

    # reset votes and login
    user_votes = load_user_votes()
    user_login = load_user_login()
    reset_votes = {}
    for uid,details in user_votes.items():
        reset_votes[uid] = details
        reset_votes[uid]["voted"] = 0
    reset_login = {}
    for uid,details in user_login.items():
        reset_login[uid] = details
        reset_login[uid]["loggedin"] = 0
    save_users_vote(reset_votes)
    save_users_login(reset_login)
    print("RESET VOTES AND LOGIN")

    # change question
    questions_bank = load_question_bank() # load
    used_questions = {}
    for qid, details in questions_bank.items():
        if details["Status"] == 2:
            used_questions[qid] = details

    ystd_question = {}
    ystd_question_id = ""
    for qid, details in questions_bank.items():
        if details["Status"] == 1:
            ystd_question[qid] = details
            ystd_question_id = qid

    unused_questions = {}
    unused_question_ids = []
    for qid, details in questions_bank.items():
        if details["Status"] == 0:
            unused_questions[qid] = details
            unused_question_ids.append(qid)

    ystd_question[ystd_question_id]["Status"] = 2
    
    # select question randomly
    new_question_id = random.choice(unused_question_ids)
    # change
    unused_questions[new_question_id]["Status"] = 1 # set for today's Q
    print(f"New question: {unused_questions[new_question_id]['Question']}")
    all_questions = {}
    # update
    all_questions.update(unused_questions)
    all_questions.update(ystd_question)
    all_questions.update(used_questions)
    save_questions(all_questions) # save

    set_daily_question() # cache after save

    # reset comments

    comments = {"04/01/2025 10:09:20":{
            "GameMaster":"Let the poll begin!"
        }}
    save_comments(comments) # reset comments
