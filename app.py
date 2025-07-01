from flask import Flask, render_template, redirect, url_for, request, session, flash, send_from_directory, jsonify
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from datetime import datetime, date
import qrcode
import os

app = Flask(__name__)
app.config.from_pyfile('config.py')

# Uploads directory
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)

# Serve uploaded employee photos and QR codes
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Login Route
@app.route('/', methods=['GET', 'POST'])
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
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid login credentials", "danger")

    return render_template('login.html')

# Dashboard - List Employees
@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    search = request.args.get('search', '').strip()
    cur = mysql.connection.cursor()

    if search:
        query = """
        SELECT * FROM employees
        WHERE name LIKE %s OR username LIKE %s OR city LIKE %s
        """
        wildcard = f"%{search}%"
        cur.execute(query, (wildcard, wildcard, wildcard))
    else:
        cur.execute("SELECT * FROM employees")

    data = cur.fetchall()
    cur.close()
    return render_template('dashboard.html', users=data)

# QR Attendance Scan Page Route
@app.route('/scan')
def scan():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template('scan.html')

# Attendance Marking API
@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    employee_id = data['employee_id']
    today = date.today()
    now_time = datetime.now().time()

    cur = mysql.connection.cursor()
    # Check today's attendance
    cur.execute("SELECT * FROM attendance WHERE employee_id=%s AND date=%s", (employee_id, today))
    record = cur.fetchone()

    if not record:
        # Sign In
        cur.execute("INSERT INTO attendance (employee_id, date, sign_in, sign_out) VALUES (%s, %s, %s, %s)",
                    (employee_id, today, now_time, None))
        mysql.connection.commit()
        status = "Signed In"
    elif record and record[4] is None:
        # Sign Out
        cur.execute("UPDATE attendance SET sign_out=%s WHERE id=%s", (now_time, record[0]))
        mysql.connection.commit()
        status = "Signed Out"
    else:
        status = "Already Signed Out Today"

    cur.close()
    return jsonify({"status": status, "time": now_time.strftime('%H:%M:%S')})

# Attendance Dashboard Route
@app.route('/attendance_dashboard')
def attendance_dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

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

# Add Employee with QR Code generation
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        city = request.form['city']
        photo = request.files['photo']

        filename = ""
        if photo and photo.filename != '':
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cur = mysql.connection.cursor()
        # Insert employee first to get ID
        cur.execute("INSERT INTO employees (name, username, email, password, city, photo) VALUES (%s, %s, %s, %s, %s, %s)",
                    (name, username, email, password, city, filename))
        mysql.connection.commit()

        employee_id = cur.lastrowid

        # Generate QR code for employee ID
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(str(employee_id))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        qr_filename = f"{employee_id}_qrcode.png"
        qr_path = os.path.join(app.config['UPLOAD_FOLDER'], qr_filename)
        img.save(qr_path)

        cur.close()
        flash("Employee added with QR code!", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_employee.html')

# Edit Employee
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        city = request.form['city']
        cur.execute("UPDATE employees SET name=%s, email=%s, city=%s WHERE id=%s", (name, email, city, id))
        mysql.connection.commit()
        cur.close()
        flash("Updated Successfully!", "success")
        return redirect(url_for('dashboard'))

    cur.execute("SELECT * FROM employees WHERE id=%s", (id,))
    data = cur.fetchone()
    cur.close()
    return render_template('edit_employee.html', user=data)

# Delete Employee
@app.route('/delete/<int:id>')
def delete(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM employees WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    flash("Deleted Successfully!", "success")
    return redirect(url_for('dashboard'))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
