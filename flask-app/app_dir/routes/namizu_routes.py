from flask import Blueprint, render_template, request, redirect, jsonify, url_for, session, flash, get_flashed_messages, send_from_directory
from app_dir.utils.namizu_utils import save_comments, save_daily_poll, save_history, save_users_login, save_users_vote, save_visit_count, save_new_question, save_drawing
from app_dir.utils.namizu_utils import load_user_creds, load_user_login, load_user_votes, load_visit_count, load_drawings
from app_dir.utils.namizu_utils import load_today_poll, load_comments, load_question_bank, load_history, load_user_streak
from app_dir.utils.namizu_utils import get_daily_question, get_new_question_id, get_vote_count, get_daily_results,get_comments_packet
from app_dir.utils.namizu_utils import get_user_names, get_drawings_by_matching_day, get_questions_for_admin
from app_dir.utils.namizu_utils import daily_routine

from datetime import datetime
import random
import base64
import json
import os
import re

bp = Blueprint('namizu', __name__, template_folder='templates')

@bp.errorhandler(404)
def page_not_found404(e):
    return render_template('namizu/404.html'), 404

@bp.errorhandler(500)
def page_not_found500(e):
    return render_template('namizu/500.html'), 500

@bp.errorhandler(400)
def page_not_found400(e):
    return render_template('namizu/400.html'), 400

def check_user_logged_in(funcName) -> tuple[bool, str]:
    print(f"{session = }")
    userName = ""
    if "user" in session:
        userName = session["user"]
        return True,userName
    else:
        session['url'] = funcName
        return False,userName

@bp.route("/index")
@bp.route("/")
def index():
    alreadyLoggedIn, userName = check_user_logged_in("index")
    return render_template('/namizu/landing_page.html', userName=userName, alreadyLoggedIn=alreadyLoggedIn)

@bp.route("/poll", methods=['GET', 'POST'])
def poll():
    alreadyLoggedIn, userName = check_user_logged_in("poll")
    if not alreadyLoggedIn:
        return redirect(url_for('namizu.login'))

    daily_poll = get_daily_question()
    question = daily_poll["Question"]
    question_type = daily_poll["Type"]
    options = list(daily_poll["Answers"].keys())
    results = get_daily_results()
    vote_stat = load_user_votes()
    answers_ser_num = {}
    counter = 1
    is_poll_multichoice = False

    #* exclude
    for key, value in daily_poll["Answers"].items():
        answers_ser_num[counter] = {"key":key,"value":value}
        counter+=1

    #* exclude
    vote_stats = {}
    for value in vote_stat.values():
        vote_stats[value["name"]] = value["voted"]

    vote_count = get_vote_count()
    submitted = False # if user submitted the form
    if "user" in session:
        userName = session["user"]
    comments_packet = get_comments_packet()

    if "M" in question_type: # multichoice
        is_poll_multichoice = True

    if vote_stats[userName] == 1: # already voted
        submitted = True

    if request.method == 'GET':    
        pass        

    elif request.method == 'POST':
        if vote_count == 7: # all voted
            submitted = True
        if 'vote' in request.form and not submitted:
            if is_poll_multichoice:

                #* exclude
                for opt in range(len(options)):
                    if str(opt+1) in request.form:
                        answers_ser_num[opt+1]["value"] += 1
                
                #* exclude
                for details in answers_ser_num.values():
                    daily_poll["Answers"][details["key"]] = details["value"]

                save_daily_poll(daily_poll)
                vote_stats[userName] = 1 # submitted vote
                vote_stat = load_user_votes()
                new_vote_stats = vote_stat.copy()

                #* exclude
                for uid, details in vote_stat.items():
                    for name,vote in vote_stats.items():
                        if details["name"] == name:
                            new_vote_stats[uid]["voted"] = vote

                save_users_vote(new_vote_stats)
                submitted = True
            else:    
                choice = request.form['vote']
                daily_poll["Answers"][choice] += 1

                save_daily_poll(daily_poll)
                vote_stats[userName] = 1 # submitted vote
                vote_stat = load_user_votes()
                new_vote_stats = vote_stat.copy()

                #* exclude
                for uid, details in vote_stat.items():
                    for name,vote in vote_stats.items():
                        if details["name"] == name:
                            new_vote_stats[uid]["voted"] = vote

                save_users_vote(new_vote_stats)
                submitted = True

        if 'comment' in request.form:
            comment = request.form['comment']
            if "user" in session:
                userName = session["user"]
            current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            user_comments = load_comments()
            user_comments[current_date] = {
                userName: comment
            }
            save_comments(user_comments)
            comments_packet = get_comments_packet()
            return redirect(url_for('namizu.poll'))
    
    #* exclude
    results_raw = daily_poll["Answers"]
    results = []
    for k,v in results_raw.items():
        results_temp = {}
        results_temp["label"] = k
        results_temp["value"] = v
        results_temp["width"] = int(v/7*100)
        results.append(results_temp)

    vote_stat = load_user_votes()
    vote_count = get_vote_count()
    return render_template('namizu/poll.html', question=question, is_poll_multichoice=is_poll_multichoice,
                           options=options, results=results, form_submitted=submitted,
                           player_num=7, vote_count=vote_count, comments=comments_packet)

@bp.route("/calendar")
def calendar():
    alreadyLoggedIn, userName = check_user_logged_in("calendar")
    if not alreadyLoggedIn:
        return redirect(url_for('namizu.login'))
    return render_template('namizu/calendar.html')

@bp.get("/history/<target_date>")
def show_history(target_date):
    alreadyLoggedIn, userName = check_user_logged_in("show_history")
    if not alreadyLoggedIn:
        return redirect(url_for('namizu.login'))
    is_poll_multichoice = False
    results = []
    comments_packet = []
    vote_count = 0
    player_count = 7
    history = load_history()
    date_obj = datetime.strptime(target_date, "%Y-%m-%d")
    target_date_uk_format = date_obj.strftime("%d-%m-%Y")
    if target_date_uk_format in history:
        history_log = history[target_date_uk_format]

        results_raw = history_log["Answers"]
        
        if "Voted" in history_log:
            for v in history_log["Voted"].values():
                vote_count += v["voted"]
        else:
            vote_count = sum(history_log["Answers"].values())
        
        #* exclude
        for k,v in results_raw.items():
            results_temp = {}
            results_temp["label"] = k
            results_temp["value"] = v
            results_temp["width"] = int(v/7*100)
            results.append(results_temp)

        if "M" in history_log["Type"]: # multichoice
            is_poll_multichoice = True
        
        comments_packet = history_log["Comments"]
    else:
        return render_template('namizu/missing_history_log.html')
        
    return render_template('namizu/wayback_machine.html',question=history_log["Question"], 
                           results=results, vote_count=vote_count, 
                           player_num=player_count, comments=comments_packet, date=target_date_uk_format)

@bp.route('/login', methods=['GET', 'POST'])
def login():  
    creds = load_user_creds()
    logins = load_user_login()
    options = list(creds.keys())

    #* exclude
    streaks_all = load_user_streak()
    streaks = {}
    for uid,details in streaks_all.items():
        if details["streak"] > 0:
            streaks[details["name"]] = details["streak"]

    if request.method == "POST":
        user = request.form["vote"]
        password = request.form["password"]
        if creds[user] == password:
            visit_count = load_visit_count()
            visit_count["total"] += 1 # one more visitor
            save_visit_count(visit_count)
            session["user"] = user
            session.modified = True
            for uid,details in logins.items():
                if details["name"] == user:
                    logins[uid]["loggedin"] = 1
                    break
            save_users_login(logins)
            if 'url' in session:
                print()
                return redirect(url_for(f"namizu.{session['url']}"))
    return render_template('namizu/login.html',options=options, streak=streaks)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("namizu.index"),302)

@bp.route('/editor', methods=['GET', 'POST'])
def editor():
    alreadyLoggedIn, userName = check_user_logged_in("editor")
    if not alreadyLoggedIn:
        return redirect(url_for('namizu.login'))
    session.pop('_flashes', None)
    # define variables
    question = ""
    answers = []
    options = []
    qid = 0
    new_question_body = {}
    temp_q = {}
    names = get_user_names()
    submitPoll = False
    do_restart = False
    select_mode = ""
    option_mode = ""

    ### V / D
    variable_in_question = False 
    multichoice = False #
    names_as_options = False
    yes_or_no = False

    # question types:

    # Variable in question: V
    # No variable in question: D

    # Single choice: S
    # Multichoice: M

    # Names as options: N
    #   put X at the end
    # Custom options as options: C
    #   Yes or no answers: Y
    #   Open-ended answers: O

    # type example: DMNX

    #* restart if M and CY in type

    poll_type = ""

    if request.method == "GET":
        pass
    
    if request.method == "POST":

        question = request.form["question"]
        if "{" in question and "}" in question:
            variable_in_question = True
        select_mode = request.form['radio-selection']
        if select_mode == "multiple":
            multichoice = True
        option_mode = request.form['radio-options']
        if option_mode == "names":
            names_as_options = True
        answers = []   
        if names_as_options:
            answers = names
        else:
            for key, val in request.form.items():
                if key.startswith("answer"):
                    answers.append(val)
        if not names_as_options:
            if "yes" in [a.lower() for a in answers] or "no" in [a.lower() for a in answers]:
                yes_or_no = True

        poll_type = ""
        poll_type += "V" if variable_in_question else "D"
        poll_type += "M" if multichoice else "S"
        poll_type += "N" if names_as_options else "C"

        if not names_as_options:
            if yes_or_no:
                poll_type += "Y"
            else:
                poll_type += "O"
        else:
            poll_type += "X" # names, therefore yes or no is irrelevant
     
        if variable_in_question:
                
            text = question
            number_of_variables = text.count("{")
                # Names to replace
            selected_names = random.sample(names, number_of_variables)
                # Replace placeholders sequentially
            result = re.sub(r"{P}", lambda _: selected_names.pop(0), text)
            question = result           
            
        if not names_as_options:
            options = answers
            for option in options:
                if option == "":
                    do_restart = True
                    flash("Some options are empty. Session restarted")

        if multichoice and yes_or_no:
            do_restart = True
            flash("Cannot be YesOrNo and Multichoice at the same time. Session restarted")

        if question == "":
            do_restart = True
            flash("No question included. Session restarted")
        if not answers:
            do_restart = True
            flash("No answers included. Session restarted")
        
        answers = {key:0 for key in answers}

        submitPoll = True

        #* exclude
        qid = get_new_question_id()
        qid = "Q"+str(qid)
        new_question_body = {
            "Type": poll_type,
            "Question": question,
            "Answers": answers,
            "Status": 0
        }
        temp_q[qid] = new_question_body

    # add final check before submit question:
    # if exact question, exact type and exact answers exist, then do_restart

    questions_bank = load_question_bank()
    for details in questions_bank.values():
        if details["Question"] == question and details["Answers"] == answers and details["Type"] == poll_type:
            do_restart = True
            flash("Poll already exists. Session restarted.")
            break
    
    if not do_restart and submitPoll:
        for k,v in temp_q.items():
            save_new_question(k,v)
            break
        flash("Submitted successfully.")

    return render_template('namizu/editor.html', namesList=names)
    
@bp.route("/admin")
def namizu_admin():
    if "user" in session:
        if session["user"] != "Geri":
            return redirect(url_for('namizu.index'))
    else:
        return redirect(url_for('namizu.index'))
    visits = load_visit_count()
    visits = visits["total"]
    questions_bank = load_question_bank()

    #* exclude
    logins = load_user_login()
    loginers = []
    for v in logins.values():
        if v["loggedin"] == 1:
            loginers.append(v["name"])

    if loginers:
        loginers = ', '.join(loginers)
    else:
        loginers = "No one"

    #* exclude
    used_questions = 0
    for details in questions_bank.values():
        if details["Status"] == 2:
            used_questions += 1

    return render_template('namizu/admin.html', visits=visits, loginers=loginers,used_questions=used_questions,
                           num_of_questions=len(questions_bank))

@bp.route("/admin/questions")
def questions_list():
    if "user" in session:
        if session["user"] != "Geri":
            return redirect(url_for('namizu.index'))
    else:
        return redirect(url_for('namizu.index'))
    
    questions = get_questions_for_admin()
    return render_template('namizu/questions_list.html', questions=questions) 

@bp.route("/reset")
def admin_reset():
    if "user" in session:
        if session["user"] != "Geri":
            return redirect(url_for('namizu.index'))
    else:
        return redirect(url_for('namizu.index'))
    daily_routine()
    return redirect(url_for('namizu.index'))

@bp.route("/sketcher/canvas")
def sketcher_canvas():
    alreadyLoggedIn, userName = check_user_logged_in("sketcher_canvas")
    if not alreadyLoggedIn:
        return redirect(url_for('namizu.login'))
    return render_template("namizu/sketcher_canvas.html")

@bp.route("/sketcher/save", methods=['GET', 'POST'])
def sketcher_save():
    image_data = ""
    image_title = ""
    image_descr = ""
    image_author = ""
    image_date = ""
    directory_path = "uploads"
    if request.method == "POST":
        image_data = request.form.get('imageData')
        image_title = request.form.get('title')
        image_descr = request.form.get('descr')
        image_author = session["user"]
        image_date = "2025" #datetime.now().strftime("%Y") #! hardcoded date
    if image_data:
        # Decode the base64 image
        header, encoded = image_data.split(',', 1)
        image_data = base64.b64decode(encoded)

        success = save_drawing(directory_path,image_data,image_author,image_title,image_date,image_descr)
        if success == 0:
            print(f"Image saved")
        return redirect(url_for('namizu.index'))
    return "No image data received!", 400

@bp.route("/gallery/welcome")
def gallery_welcome():
    alreadyLoggedIn, userName = check_user_logged_in("gallery_welcome")
    if not alreadyLoggedIn:
        return redirect(url_for('namizu.login'))
    
    drawing_sum = len(os.listdir("uploads"))
    drawings = load_drawings()
    authors = {item["author"] for item in drawings.values()}
    authors_names = ', '.join(authors)
    return render_template("namizu/gallery_welcome.html", drawing_sum=drawing_sum, name=userName, authors=authors_names)

@bp.route("/gallery/lift")
def gallery_lift():
    alreadyLoggedIn, userName = check_user_logged_in("gallery_lift")
    if not alreadyLoggedIn:
        return redirect(url_for('namizu.login'))

    flash_message = "Select Floor"
    #! buttons hardcoded
    buttons = [{"day":"X","month":"HOME"},
               {"day":16,"month":"JAN"},
               {"day":17,"month":"JAN"},
               {"day":18,"month":"JAN"},
               {"day":19,"month":"JAN"},
               {"day":20,"month":"JAN"},
               {"day":21,"month":"JAN"},
               {"day":22,"month":"JAN"},
               {"day":23,"month":"JAN"},
               {"day":24,"month":"JAN"},
               {"day":25,"month":"JAN"},
               {"day":26,"month":"JAN"},
               {"day":27,"month":"JAN"},
               {"day":28,"month":"JAN"},
               {"day":29,"month":"JAN"},
               {"day":30,"month":"JAN"},
               {"day":31,"month":"JAN"},
               {"day":1,"month":"FEB"},
               {"day":2,"month":"FEB"},
               {"day":3,"month":"FEB"},
               {"day":4,"month":"FEB"},
               {"day":5,"month":"FEB"},
               {"day":6,"month":"FEB"},
               {"day":7,"month":"FEB"},
               {"day":8,"month":"FEB"},
               {"day":9,"month":"FEB"},
               {"day":10,"month":"FEB"}]
    flash_messages = get_flashed_messages()
    if flash_messages:
        flash_message = flash_messages[0]
    get_flashed_messages()
    session.pop('_flashes', None)
    return render_template("namizu/gallery_lift.html", buttons=buttons, flash_message=flash_message)

@bp.route('/uploads/<filename>')
def serve_uploads(filename):
    return send_from_directory("../uploads", filename)

@bp.route("/gallery/<target_date>")
def gallery_day(target_date):
    alreadyLoggedIn, userName = check_user_logged_in("gallery_day")
    if not alreadyLoggedIn:
        return redirect(url_for('namizu.login'))

    directory_path = "uploads"
    date_found = False
    drawings_dir = os.listdir(directory_path)
    art_db = load_drawings()  
    target_day_n_month = target_date.split("-")
    date_str = f"{target_day_n_month[0]} {target_day_n_month[1]} 2025" #! hardcoded year
    date_obj = datetime.strptime(date_str, "%d %b %Y")
   
    screenshots,date_found = get_drawings_by_matching_day(art_db,drawings_dir,date_obj,date_found)

    if not date_found:
        get_flashed_messages()
        session.pop('_flashes', None)
        flash(f"Floor {date_obj.day} {date_obj.strftime('%b')} is empty")
        return redirect(url_for('namizu.gallery_lift'))
    return render_template("namizu/gallery_swiper.html", screenshots=screenshots)