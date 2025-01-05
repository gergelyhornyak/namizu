from flask import Blueprint, render_template, request, redirect, jsonify, url_for, session, flash
from app_dir.utils.askus_utils import load_question_bank, load_scores, save_scores, save_questions, get_daily_question,load_user_status, save_player_stat, load_user_creds, load_visit_count, save_visit_count, load_comments, save_comments
import random
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

bp = Blueprint('askus', __name__, template_folder='templates')

@bp.route("/")
def index():
    return render_template('askus_landing_page.html')

@bp.route("/poll", methods=['GET', 'POST'])
def main():
    question = get_daily_question()
    scores = load_scores()
    options = scores.keys()
    results = {}
    stats = load_user_status()
    vote_count = sum(scores.values())
    player_count = len(scores)
    vote_percentage = int(vote_count/player_count*100)
    submitted = False # if user submitted the form
    user = session["user"]
    user_comments = load_comments()
    comments_packet = []
    for timestamp, comments in user_comments.items():
        for usern, message in comments.items():
            comments_packet.append({"name": usern, "message": message})
    
    if request.method == 'GET':    
        if stats[user] == 2: # already voted
            submitted = True
        results = scores
        vote_count = sum(scores.values())
        vote_percentage = int(vote_count/player_count*100)
    elif request.method == 'POST':
        if vote_count == player_count:
            results = scores
            vote_count = sum(scores.values())
            vote_percentage = int(vote_count/player_count*100)
            submitted = True
        else:
            if 'vote' in request.form:
                choice = request.form['vote']
                scores[choice] += 1
                save_scores(scores)
                submitted = True
                stats[user] = 2 # submitted vote
                save_player_stat(stats)
                results = scores
                vote_count = sum(scores.values())
                vote_percentage = int(vote_count/player_count*100)
        if 'comment' in request.form:
            submitted = True
            comment = request.form['comment']
            user = session["user"]
            results = scores
            vote_count = sum(scores.values())
            vote_percentage = int(vote_count/player_count*100)
            current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            user_comments[current_date] = {
                user: comment
            }
            save_comments(user_comments)
            comments_packet = []
            for timestamp, comments in user_comments.items():
                for usern, message in comments.items():
                    comments_packet.append({"name": usern, "message": message})
            
    return render_template('askus_main.html', question=question, options=options, 
                           vote_count=vote_count, results=results, form_submitted=submitted, 
                           player_num=player_count, comments=comments_packet)

@bp.route("/snapshot")
def poll_snapshot():
    question = get_daily_question()
    scores = load_scores()
    options = scores.keys()
    results = scores
    user_comments = load_comments()
    comments_packet = []
    vote_count = sum(scores.values())
    player_count = len(scores)
    current_date = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    for timestamp, comments in user_comments.items():
        for usern, message in comments.items():
            comments_packet.append({"name": usern, "message": message})
    return render_template('poll_snapshot.html', question=question, options=options, 
                           vote_count=vote_count, results=results, player_num=player_count, comments=comments_packet, date=current_date)

@bp.route("/emulate_calendar")
def emulate_calendar():
    # user can select date on calendar widget, 
    #  then date is queried from history, 
    #   then poll_snapshot is rendered with history data
    return "<h1>Being developed ...</h1>"

@bp.route("/calendar")
def calendar():
    # very neat approach, however not sustainable, 
    # as too many screenshots are created: 200KB * 365 = 72MB
    # also too long comments are not visible
    directory = "app_dir/static/screenshots"
    png_files = [file for file in os.listdir(directory) if file.endswith(".png")]
    screenshots = png_files

    return render_template('calendar.html', screenshots=screenshots)

@bp.route("/ss")
def screenShot():
    return "OUT OF ORDER"
    mobile_emulation = {
        "deviceName": "Pixel 7"
    }
    chrome_options = Options()
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("http://127.0.0.1:5000/askus/snapshot")
        current_date = datetime.now().strftime("%d-%m-%Y")
        driver.save_screenshot(f"app_dir/static/screenshots/{current_date}_shot.png")
        print(f"{current_date}_shot.png saved.")
    finally:
        driver.quit()
    return redirect(url_for("askus.index"),302)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    options = load_user_status()
    creds = load_user_creds()
    session["user"] = "noone"
    session.modified = True
    if request.method == "POST":
        visit_count = load_visit_count()
        visit_count["total"] += 1 # one more visitor
        save_visit_count(visit_count)
        user = request.form["vote"]
        password = request.form["password"]
        if creds[user] == password:
            session["user"] = user
            session.modified = True
            return redirect(url_for("askus.main"),302)

    return render_template('askus_login.html',options=options)

@bp.route('/append', methods=['GET', 'POST'])
def append_q():
    return "ALMOST FINISHED"
    if request.method == "POST":
        new_question = request.form["question"]
        new_answers = request.form["answers"]
        print(f"{new_question = }")
        print(f"{new_answers = }")
    return render_template('askus_new_question.html')

@bp.route('/reset')
def reset_scores():
    return "ADMIN PERMISSION REQUIRED"
    scores = load_scores()
    questions = load_question_bank()
    stats = load_user_status()
    zero_scores = {key: 0 for key in scores}
    zero_questions = {key: 0 for key in questions}
    rnd_question = random.choice(list(zero_questions.items()))[0]
    zero_questions[rnd_question] = 1
    zero_stats = {key: 0 for key in stats}
    save_scores(zero_scores)
    save_questions(zero_questions)
    save_player_stat(zero_stats)
    
    return redirect(url_for('askus.index'))

@bp.route("/visits")
def page_visits():
    visits = load_visit_count()
    visits = visits["total"]
    return f"<p>naMizu has been visited {visits} times so far.</p>"