from flask import Blueprint, render_template, send_file
from models.employee import EmployeeModel
from models.attendance import AttendanceModel
import pandas as pd
from fpdf import FPDF
import os

report_bp = Blueprint('report', __name__)

EXPORT_FOLDER = os.path.join(os.getcwd(), 'exports')
if not os.path.exists(EXPORT_FOLDER):
    os.makedirs(EXPORT_FOLDER)

@report_bp.route('/reports/employees')
def employee_report():
    employees = EmployeeModel.get_all('')
    return render_template('employee_report.html', users=employees)

@report_bp.route('/reports/employees/export/<string:format>')
def export_employee_report(format):
    employees = EmployeeModel.get_all('')
    df = pd.DataFrame(employees, columns=['ID', 'Name', 'Username', 'Email', 'Password', 'City', 'Photo'])

    filename = os.path.join(EXPORT_FOLDER, f"employee_report.{format}")

    if format == 'xlsx':
        df.to_excel(filename, index=False)
    elif format == 'pdf':
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for index, row in df.iterrows():
            line = f"{row['ID']} | {row['Name']} | {row['Username']} | {row['Email']} | {row['City']}"
            pdf.cell(200, 10, txt=line, ln=True)
        pdf.output(filename)
    else:
        return "Invalid format"

    return send_file(filename, as_attachment=True)

@report_bp.route('/reports/attendance')
def attendance_report():
    records = AttendanceModel.all_attendance()
    return render_template('attendance_report.html', records=records)

@report_bp.route('/reports/attendance/export/<string:format>')
def export_attendance_report(format):
    records = AttendanceModel.all_attendance()
    df = pd.DataFrame(records, columns=['Name', 'Date', 'Sign In', 'Sign Out'])

    filename = os.path.join(EXPORT_FOLDER, f"attendance_report.{format}")

    if format == 'xlsx':
        df.to_excel(filename, index=False)
    elif format == 'pdf':
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for index, row in df.iterrows():
            line = f"{row['Name']} | {row['Date']} | {row['Sign In']} | {row['Sign Out']}"
            pdf.cell(200, 10, txt=line, ln=True)
        pdf.output(filename)
    else:
        return "Invalid format"

    return send_file(filename, as_attachment=True)
