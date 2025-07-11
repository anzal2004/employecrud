from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import mysql

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and user[4] == password_input:
            session['loggedin'] = True
            session['username'] = user[2]
            return redirect(url_for('employee.dashboard'))
        else:
            flash("Invalid login credentials", "danger")

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
