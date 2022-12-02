import functools
from hashlib import md5

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from DatabaseAPI import Database

auth = Blueprint('auth', __name__, url_prefix='/auth')


# @bp.route('/register', methods=('GET', 'POST'))
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#
#         db = Database
#         error = None
#
#         if not username:
#             error = 'Username is required.'
#         elif not password:
#             error = 'Password is required.'
#
#         if error is None:
#             try:
#                 pass
#                 #db.set_user()
#             # except
#         else:
#             return redirect(url_for('auth.login'))
#
#         flash(error)
#         return render_template('auth/register.html')

@auth.route('/login', methods=('POST', 'GET'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # allow login w/o db connection
        if (username, password) == ("admin", "admin"):
            session.clear()
            session['user_id'] = 0
            return redirect(url_for('index'))

        db = Database()
        error = None
        user = db.get_user(username, password)

        if user is None:
            error = "Username or password wrong"

        if error is None:
            session.clear()
            session['user_id'] = user['uid']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@auth.before_app_request
def load_logged_in_user():
    """checks if a user id is stored in the session and gets that user's data from database, storing it in g.user"""
    user_id = session.get('user_id')
    db = Database()
    # user_id = 0
    if user_id == 0:
        g.user = {
            "uid": 0,
            "fname": "admin",
            "lname": "admin",
            "login": "admin",
            "pw": f"{md5('admin'.encode()).hexdigest()}"
        }
        return

    if user_id is None:
        g.user = None
    else:
        g.user = db.get_user_by_id(user_id)


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


def login_required(view):
    """wraps around other fucntions to check if user is logged in. If not, redirect to log-in"""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
