from flask import Blueprint, render_template, request, flash, redirect
from app_dir.utils.gamechanger_utils import load_page_values, save_page_values

bp = Blueprint('gamechanger', __name__, template_folder='templates')

@bp.route('/')
def main():
    return render_template('gchome.html')

@bp.route('/apple')
def apple():
    page_values = load_page_values()
    return render_template('apple.html', value=page_values["apple"])

@bp.route('/banana')
def banana():
    page_values = load_page_values()
    return render_template('banana.html', value=page_values["banana"])

@bp.route('/coconut')
def coconut():
    page_values = load_page_values()
    return render_template('coconut.html', value=page_values["coconut"])

@bp.route('/dates')
def dates():
    page_values = load_page_values()
    return render_template('dates.html', value=page_values["dates"])

@bp.route('/admin', methods=['GET', 'POST'])
def admin():
    page_values = load_page_values()
    if request.method == 'POST':
        for key in ['apple', 'banana', 'coconut', 'dates']:
            page_values[key] = int(request.form[f'{key}_new'])
        save_page_values(page_values)
        flash("Updated scores.")
        return redirect('/gamechanger/admin')
    return render_template('admin.html', page_values=page_values)

@bp.route("/maze")
def maze():
    return render_template("minigame.html")

@bp.route("/wof")
def wof():
    return render_template("wheel_of_fortune.html")

@bp.route("/wofreal")
def wof_real():
    return render_template("wheel_of_fortune_real.html")

@bp.route("/quiz")
def game():
    return render_template("game01.html")

@bp.route("/loop1")
def loop1():
    return render_template("loop1.html")
