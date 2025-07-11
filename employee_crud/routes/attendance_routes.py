from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from extensions import mysql
from datetime import datetime, date

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance_dashboard')
def attendance_dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    today = date.today()
    cur = mysql.connection.cursor()

    # Total present today
    cur.execute("SELECT COUNT(*) FROM attendance WHERE date=%s", (today,))
    present_count = cur.fetchone()[0]

    # Total employees
    cur.execute("SELECT COUNT(*) FROM employees")
    total_employees = cur.fetchone()[0]

    absent_count = total_employees - present_count

    # Fetch today's attendance records
    cur.execute("""
    SELECT e.name, a.sign_in, a.sign_out
    FROM attendance a
    JOIN employees e ON a.employee_id = e.id
    WHERE a.date = %s
    """, (today,))
    records = cur.fetchall()
    cur.close()

    return render_template('attendance_dashboard.html',
                           present=present_count,
                           absent=absent_count,
                           records=records)

# AJAX endpoint for attendance
@attendance_bp.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    employee_id = data['employee_id']
    today = date.today()
    now_time = datetime.now().time()

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM attendance WHERE employee_id=%s AND date=%s", (employee_id, today))
    record = cur.fetchone()

    if not record:
        cur.execute("INSERT INTO attendance (employee_id, date, sign_in, sign_out) VALUES (%s, %s, %s, %s)",
                    (employee_id, today, now_time, None))
        mysql.connection.commit()
        status = "Signed In"
    elif record and record[4] is None:
        cur.execute("UPDATE attendance SET sign_out=%s WHERE id=%s", (now_time, record[0]))
        mysql.connection.commit()
        status = "Signed Out"
    else:
        status = "Already Signed Out Today"

    cur.close()
    return jsonify({"status": status, "time": now_time.strftime('%H:%M:%S')})
