from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from extensions import mysql
from models.employee import EmployeeModel
import os

# Blueprint configuration
employee_bp = Blueprint('employee', __name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

# Dashboard route
@employee_bp.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    search = request.args.get('search', '').strip()
    employees = EmployeeModel.get_all(search)
    return render_template('dashboard.html', users=employees)

# Add employee route
@employee_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        EmployeeModel.add_employee(request.form, request.files['photo'])
        flash("Employee added with QR code!", "success")
        return redirect(url_for('employee.dashboard'))

    return render_template('add_employee.html')

# Edit employee route
@employee_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        EmployeeModel.update_employee(id, request.form)
        flash("Updated Successfully!", "success")
        return redirect(url_for('employee.dashboard'))

    user = EmployeeModel.get_by_id(id)
    return render_template('edit_employee.html', user=user)

# Delete employee route
@employee_bp.route('/delete/<int:id>')
def delete(id):
    EmployeeModel.delete_employee(id)
    flash("Deleted Successfully!", "success")
    return redirect(url_for('employee.dashboard'))

# Serve uploaded files (photos, QR codes)
@employee_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ✅ Added Scan route to fix BuildError
@employee_bp.route('/scan')
def scan():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))
    return render_template('scan.html')

# ✅ Added Attendance Dashboard route for completeness (if used in templates)
@employee_bp.route('/attendance_dashboard')
def attendance_dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    from models.attendance import AttendanceModel
    records = AttendanceModel.today_attendance()
    return render_template('attendance_dashboard.html', records=records)
