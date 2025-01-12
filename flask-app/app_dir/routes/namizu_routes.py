from flask import Blueprint, render_template, request, redirect, jsonify, url_for, session, flash, get_flashed_messages
from app_dir.utils.namizu_utils import save_comments, save_daily_poll, save_history, save_users_login, save_users_vote, save_visit_count, save_new_question
from app_dir.utils.namizu_utils import load_user_creds, load_user_login, load_user_votes, load_visit_count
from app_dir.utils.namizu_utils import load_today_poll, load_comments, load_question_bank, load_history, load_user_streak
from app_dir.utils.namizu_utils import get_daily_question, get_new_question_id, get_vote_count, get_daily_results,get_comments_packet, get_user_names
from app_dir.utils.namizu_utils import daily_routine
from datetime import datetime
import random
import json
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

@bp.route("/")
def index():
    alreadyLoggedIn = False
    userName = ""
    if "user" in session:
        userName = session["user"]
        alreadyLoggedIn = True
    return render_template('/namizu/landing_page.html', userName=userName, alreadyLoggedIn=alreadyLoggedIn)

@bp.route("/poll", methods=['GET', 'POST'])
def main():
    daily_poll = get_daily_question()
    question = daily_poll["Question"]
    question_type = daily_poll["Type"]
    options = list(daily_poll["Answers"].keys())
    results = get_daily_results()
    vote_stat = load_user_votes()
    answers_ser_num = {}
    counter = 1
    is_poll_multichoice = False
    for key, value in daily_poll["Answers"].items():
        answers_ser_num[counter] = {"key":key,"value":value}
        counter+=1

    # exclude
    vote_stats = {}
    for value in vote_stat.values():
        vote_stats[value["name"]] = value["voted"]

    vote_count = get_vote_count()
    submitted = False # if user submitted the form
    user = session["user"]
    comments_packet = get_comments_packet()
    
    if request.method == 'GET':    
        if vote_stats[user] == 1: # already voted
            submitted = True
    elif request.method == 'POST':
        if vote_stats[user] == 1: # already voted
            submitted = True
        if vote_count == 7: # all voted
            submitted = True
        if 'vote' in request.form and not submitted:
            if "M" in question_type: # multichoice
                is_poll_multichoice = True
                for opt in range(len(options)):
                    if str(opt+1) in request.form:
                        answers_ser_num[opt+1]["value"] += 1
                for details in answers_ser_num.values():
                    daily_poll["Answers"][details["key"]] = details["value"]

                save_daily_poll(daily_poll)
                vote_stats[user] = 1 # submitted vote
                vote_stat = load_user_votes()
                new_vote_stats = vote_stat.copy()
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
                vote_stats[user] = 1 # submitted vote
                vote_stat = load_user_votes()
                new_vote_stats = vote_stat.copy()
                for uid, details in vote_stat.items():
                    for name,vote in vote_stats.items():
                        if details["name"] == name:
                            new_vote_stats[uid]["voted"] = vote
                save_users_vote(new_vote_stats)
                submitted = True

        if 'comment' in request.form:
            comment = request.form['comment']
            user = session["user"]
            current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            user_comments = load_comments()
            user_comments[current_date] = {
                user: comment
            }
            save_comments(user_comments)
            comments_packet = get_comments_packet()
            return redirect(url_for('namizu.main'))
    
    daily_poll = get_daily_question()
    question = daily_poll["Question"]
    question_type = daily_poll["Type"]
    options = list(daily_poll["Answers"].keys())
    results_raw = daily_poll["Answers"]
    results = []
    vote_stat = load_user_votes()
    vote_count = get_vote_count()
    for k,v in results_raw.items():
        results_temp = {}
        results_temp["label"] = k
        results_temp["value"] = v
        results_temp["width"] = int(v/7*100)
        results.append(results_temp)
    return render_template('namizu/main.html', question=question, multichoice=is_poll_multichoice,
                           options=options, results=results, form_submitted=submitted,
                           player_num=7, vote_count=vote_count, comments=comments_packet)

@bp.route("/calendar")
def calendar():
    return render_template('namizu/calendar.html')

@bp.get("/history/<target_date>")
def show_history(target_date):
    history = load_history()
    date_obj = datetime.strptime(target_date, "%Y-%m-%d")
    target_date_uk_format = date_obj.strftime("%d-%m-%Y")
    if target_date_uk_format in history:
        history_log = history[target_date_uk_format]
        vote_count = sum(history_log["Answers"].values())
        player_count = len(history_log["Answers"])
        comments_packet = history_log["Comments"]
    else:
        return render_template('namizu/missing_history_log.html')
        
    return render_template('namizu/wayback_machine.html',question=history_log["Question"], 
                           results=history_log["Answers"], vote_count=vote_count, 
                           player_num=player_count, comments=comments_packet, date=target_date_uk_format)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    creds = load_user_creds()
    logins = load_user_login()
    options = list(creds.keys())
    streaks_all = load_user_streak()
    streaks = {}
    for uid,details in streaks_all.items():
        if details["streak"] > 0:
            streaks[details["name"]] = details["streak"]

    if "user" in session:
        return redirect(url_for("namizu.main"),302)

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

            return redirect(url_for("namizu.main"),302)

    return render_template('namizu/login.html',options=options, streak=streaks)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("namizu.index"),302)

@bp.route('/editor', methods=['GET', 'POST'])
def editor():
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

        #return f"<h1>Poll type: {poll_type}</h1><p>{question}</p><p>{select_mode}</p><p>{option_mode}</p><p>{', '.join(answers)}</p>"
            
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
            """
            if len(options) > 6 or len(options) < 1: # too long or empty
                # restart
                do_restart = True
                flash("Too many / too few options provided. Session restarted")
            """
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
    logins = load_user_login()
    loginers = []
    for v in logins.values():
        if v["loggedin"] == 1:
            loginers.append(v["name"])
    if loginers:
        loginers = ', '.join(loginers)
    else:
        loginers = "No one"

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
    questions_bank = load_question_bank()
    questions = []
    
    for qid,q_body in questions_bank.items():
        temp_question = {}  
        temp_question["QID"] = qid
        temp_question["Question"] = q_body["Question"]
        temp_question["Answers"] = q_body["Answers"]
        temp_question["Status"] = q_body["Status"]
        questions.append(temp_question)

    return render_template('namizu/questions_list.html', questions=questions) 

@bp.route("/reset")
def admin_reset():
    return "<h1>RESTRICTED COMMAND</h1>"
    daily_routine()
    return "<h1>ADMIN RESET FINISHED</h1>"