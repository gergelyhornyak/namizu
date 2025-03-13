import json
import os
import random
from datetime import datetime, timedelta

DATABASE_PATH = "database/"

# loaders

def load_visit_count():
    try:
        with open('database/visit_count.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'total': 0}
    except Exception as e:
        print(f"{e}")

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

def load_drawings():
    try:        
        with open(f"database/drawings.json", 'r') as f:
            return json.load(f)        
    except Exception as e:
        print(e)

def loadSideQuest():
    try:        
        with open(f"database/sidequest.json", 'r') as f:
            return json.load(f)        
    except Exception as e:
        print(e)


def checkSideQuest():
    try:        
        with open(f"database/sidequest.json", 'r') as f:
            return True    
    except Exception as e:
        return False


# savers

def save_drawing(directory_path,image_data,image_author,image_title,image_date,image_descr):
    try:
        # List all entries in the directory
        entries = os.listdir(directory_path)    
        # Count files only
        file_count = sum(1 for entry in entries if os.path.isfile(os.path.join(directory_path, entry)))
        filename = file_count+1
    except FileNotFoundError:
        print(f"The directory '{directory_path}' does not exist.")
        return 1
    except PermissionError:
        print(f"Permission denied to access the directory '{directory_path}'.")
        return 2
    file_path = os.path.join(directory_path, f'drawing_{filename}.png')
    with open(file_path, 'wb') as f: f.write(image_data)
    imageJson = load_drawings()
    full_filename = f"drawing_{filename}.png"
    imageJson[full_filename] = {}
    imageJson[full_filename]['filename'] = full_filename
    imageJson[full_filename]['author'] = image_author
    imageJson[full_filename]['title'] = image_title
    if image_title == "":
        imageJson[full_filename]['title'] = "Untitled"
    imageJson[full_filename]['date'] = image_date
    imageJson[full_filename]['descr'] = image_descr
    imageJson[full_filename]['submitted'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open(f"database/drawings.json", 'w') as f:
        json.dump(imageJson, f, indent=4)  
    return 0


def save_user_db(user_db):
    with open('database/user_db.json', 'w') as f:
        json.dump(user_db, f,indent=4)

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
        json.dump(visits, f, indent=4)
    
def save_questions(questions):
    with open('database/questions_bank.json', 'w') as f:
        json.dump(questions, f, indent=4)

def save_daily_poll(daily_poll):
    with open('database/today_poll.json', 'w') as f:
        json.dump(daily_poll, f, indent=4)

def save_comments(comments):
    with open('database/comments.json', 'w') as f:
        json.dump(comments, f, indent=4)

def save_history(history_logs):
    with open('database/history.json', 'w') as f:
        json.dump(history_logs, f, indent=4)

def save_new_question(qid,q):
    questions_bank = load_question_bank()
    questions_bank[qid] = q
    if q["Question"]=="":
        return 0
    with open('database/questions_bank.json', 'w') as f:
        json.dump(questions_bank, f, indent=4)

# getters

def get_questions_for_admin():
    questions_bank = load_question_bank()
    questions = []
    for qid,q_body in questions_bank.items():
        temp_question = {}  
        temp_question["QID"] = qid
        temp_question["Question"] = q_body["Question"]
        temp_question["Answers"] = q_body["Answers"]
        temp_question["Status"] = q_body["Status"]
        questions.append(temp_question)
    return questions

def get_drawings_by_matching_day(drawing_json:dict,drawing_dir:list,today:datetime,date_found:bool):
    """
    input: drawings json data, drawing directory content, date_found boolean
    """
    screenshots = []
    for filename, details in drawing_json.items():
        submit_date = datetime.strptime(details["submitted"], "%d/%m/%Y %H:%M:%S")
        if filename not in drawing_dir:
            print("missing drawing. abort import.")
            break
        if submit_date.day == today.day and submit_date.month == today.month:
            date_found = True
            screenshot = {}
            screenshot["filename"] = filename
            screenshot["author"] = drawing_json[filename]["author"]
            screenshot["title"] = drawing_json[filename]["title"]
            screenshot["date"] = drawing_json[filename]["date"]
            screenshot["descr"] = drawing_json[filename]["descr"]
            screenshots.append(screenshot)
    return screenshots,date_found

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
    
def get_sidequest_vote_count():
    return 0

def get_user_names():
    """
    list(name01,name02)
    """
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

    # before reset login, change streak according to logins
    streaks = load_user_streak()
    user_loginn = load_user_login()
    
    for uid, details in user_loginn.items():
        if details["loggedin"] == 1:
            streaks[uid]["streak"] += 1
        elif details["loggedin"] == 0:
            streaks[uid]["streak"] = 0
            

    save_users_streak(streaks)

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
    today = datetime.now()
    if today.month == 3 and today.day == 17:
        new_question_id = "Q00"
    # change
    unused_questions[new_question_id]["Status"] = 1 # set for today's Q
    
    all_questions = {}
    # update
    all_questions.update(unused_questions)
    all_questions.update(ystd_question)
    all_questions.update(used_questions)
    save_questions(all_questions) # save

    set_daily_question() # cache after save

    # reset comments

    comments = {}
    save_comments(comments) # reset comments

    # check for sidequest

    # datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    
