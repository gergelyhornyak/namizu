from flask import Blueprint, render_template, request, redirect, jsonify, url_for, session
from app_dir.utils.askus_utils import load_question, load_scores, save_scores, get_question, save_questions, get_daily_question,load_user_status, save_player_stat

bp = Blueprint('askus', __name__, template_folder='templates')

@bp.route("/")
def index():
    return redirect(url_for("askus.login"))


@bp.route("/poll", methods=['GET', 'POST'])
def main():
    submitted = False
    question = get_daily_question()
    scores = load_scores()
    options = scores.keys()
    results = {}
    stats = load_user_status()
    print(f"{stats = }")
    vote_count = sum(scores.values())
    player_count = len(scores)
    user = session["user"]
    print(f"{user = }")
    if request.method == 'GET':    
        print(f"{stats[user] = }")
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
            print(f"new value of {stats[user] = }")
            save_player_stat(stats)
            results = scores
            vote_count = sum(scores.values())

    return render_template('askus.html', question=question, options=options, vote_count=vote_count, results=results, form_submitted=submitted, player_num=player_count)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    options = load_user_status()
    if request.method == "POST":
        choice = request.form['vote']
        #options[choice] = 1 # logged in
        #save_player_stat(options)
        session["user"] = choice
        return redirect(url_for("askus.main"))
    return render_template('askus_login.html',options=options)

@bp.route('/reset')
def reset_scores():
    scores = load_scores()
    questions = load_question()
    zero_scores = {key: 0 for key in scores}
    zero_questions = {key: 0 for key in questions}
    save_scores(zero_scores)
    save_questions(zero_questions)
    
    return redirect(url_for('askus.main'))
