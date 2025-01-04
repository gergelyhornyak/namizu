from flask import Blueprint, render_template, request, redirect, jsonify, url_for, session, flash
from app_dir.utils.askus_utils import load_question, load_scores, save_scores, save_questions, get_daily_question,load_user_status, save_player_stat, load_user_creds, load_visit_count, save_visit_count
import random

bp = Blueprint('askus', __name__, template_folder='templates')

@bp.route("/")
def index():
    return render_template('askus_landing_page.html')

@bp.route("/poll", methods=['GET', 'POST'])
def main():
    submitted = False
    question = get_daily_question()
    scores = load_scores()
    options = scores.keys()
    results = {}
    stats = load_user_status()
    vote_count = sum(scores.values())
    player_count = len(scores)
    user = session["user"]
    
    if request.method == 'GET':    
        if stats[user] == 2: # already voted
            submitted = True
        results = scores
        vote_count = sum(scores.values())
    elif request.method == 'POST':
        if vote_count == player_count:
            results = scores
            vote_count = sum(scores.values())
            submitted = True
        else:
            choice = request.form['vote']
            scores[choice] += 1
            save_scores(scores)
            submitted = True
            stats[user] = 2 # submitted vote
            save_player_stat(stats)
            results = scores
            vote_count = sum(scores.values())

    return render_template('askus.html', question=question, options=options, vote_count=vote_count, results=results, form_submitted=submitted, player_num=player_count)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    options = load_user_status()
    creds = load_user_creds()
    session["user"] = "noone"
    session.modified = True
    if request.method == "POST":
        visit_count = load_visit_count()
        visit_count["total"] += 1
        save_visit_count(visit_count)
        user = request.form["vote"]
        password = request.form["password"]
        if creds[user] == password:
            session["user"] = user
            session.modified = True
            return redirect(url_for("askus.main"),302)
        else:
            flash("Incorrect password. Please try again.", "error")

    return render_template('askus_login.html',options=options)

@bp.route('/append', methods=['GET', 'POST'])
def append_q():
    if request.method == "POST":
        new_question = request.form["question"]
        new_answers = request.form["answers"]
        print(f"{new_question = }")
        print(f"{new_answers = }")
    return render_template('askus_new_question.html')

@bp.route('/reset')
def reset_scores():
    scores = load_scores()
    questions = load_question()
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