from flask import Blueprint, render_template

bp = Blueprint('main', __name__, template_folder='templates')

@bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@bp.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

@bp.route('/')
@bp.route('/home')
@bp.route('/index')
def home():
    return render_template('home.html')

@bp.route('/readme')
def readme():
    return render_template('readme.html')
