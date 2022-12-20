import functools

from flask import (Blueprint, flash, g, redirect,
                   render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']
        db = get_db()
        error = None

        byUsername = db.execute(
            'SELECT * FROM user WHERE name = ?', (user,)).fetchone()
        byCode = db.execute('SELECT * FROM user WHERE code = ?', (user,)
                            ).fetchone()
        
        exists = byUsername if byUsername is not None else byCode
        if exists is None:
            error = f"No user with username or code: {user}"
        elif not check_password_hash(exists['password'], password):
            error = "Incorrect Password"

        if error is None:
            session.clear()
            session['user_id'] = exists['id']
            return redirect(url_for('index'))
        flash(error)
    return render_template('auth/login.html')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        student_code = request.form['code']
        repeat = request.form['repeat_password']
        db = get_db()
        error = None

        if not username:
            error = "Username is required"
        elif not student_code:
            error = "Student code is required"
        elif not password:
            error = "Password is required"
        elif not repeat:
            error = "Please repeat your password"
        elif password != repeat:
            error = "Password did not match."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user(code, name, password, type) VALUES(?, ?, ?, 'user')",
                    (student_code, username, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error = f'User: {username} or Student code: {student_code} is already registered'

            else:
                return redirect(url_for("auth.login"))
        flash(error)

    return render_template('auth/register.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()


@bp.route('/logout')
def logout():
    if 'user_id' in session:
        session.clear()
        return redirect(url_for('auth.login'))
    else:
        return f"You are already logged out. <a href='" + url_for('auth.login') + "'> Log in </a>"


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
