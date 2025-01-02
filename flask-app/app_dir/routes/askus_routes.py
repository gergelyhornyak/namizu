from flask import Blueprint, render_template, request, redirect, jsonify, url_for
from app_dir.utils.askus_utils import load_question, load_scores, save_scores, get_question, save_questions, get_daily_question

bp = Blueprint('askus', __name__, template_folder='templates')

@bp.route("/", methods=['GET', 'POST'])
def main():
    submitted = False
    question = get_daily_question()
    scores = load_scores()
    options = scores.keys()
    results = {}
    vote_count = sum(scores.values())
    player_count = len(scores)
    if request.method == 'POST':
        if vote_count == player_count:
            results = scores
            vote_count = sum(scores.values())
            submitted = True
        else:
            choice = request.form['vote']
            scores[choice] += 1
            save_scores(scores)
            submitted = True
            results = scores
            vote_count = sum(scores.values())

    return render_template('askus.html', question=question, options=options, vote_count=vote_count, results=results, form_submitted=submitted, player_num=player_count)

@bp.route('/scores')
def scores():
    return jsonify(load_scores())

@bp.route('/board')
def board():
    return render_template('askus2.html')

@bp.route('/reset')
def reset_scores():
    scores = load_scores()
    questions = load_question()
    zero_scores = {key: 0 for key in scores}
    zero_questions = {key: 0 for key in questions}
    save_scores(zero_scores)
    save_questions(zero_questions)
    
    return redirect(url_for('askus.main'))
