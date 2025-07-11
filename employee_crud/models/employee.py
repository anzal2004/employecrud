import os
import qrcode
from werkzeug.utils import secure_filename
from extensions import mysql

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

class EmployeeModel:

    @staticmethod
    def get_all(search=""):
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
        return data

    @staticmethod
    def get_by_id(emp_id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM employees WHERE id=%s", (emp_id,))
        data = cur.fetchone()
        cur.close()
        return data

    @staticmethod
    def add_employee(form_data, photo_file):
        name = form_data['name']
        username = form_data['username']
        email = form_data['email']
        password = form_data['password']
        city = form_data['city']

        filename = ""
        if photo_file and photo_file.filename != '':
            filename = secure_filename(photo_file.filename)
            photo_file.save(os.path.join(UPLOAD_FOLDER, filename))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO employees (name, username, email, password, city, photo) VALUES (%s, %s, %s, %s, %s, %s)",
                    (name, username, email, password, city, filename))
        mysql.connection.commit()
        emp_id = cur.lastrowid

        # Generate QR Code for employee ID
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(str(emp_id))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        qr_filename = f"{emp_id}_qrcode.png"
        qr_path = os.path.join(UPLOAD_FOLDER, qr_filename)
        img.save(qr_path)

        cur.close()

    @staticmethod
    def update_employee(emp_id, form_data):
        name = form_data['name']
        email = form_data['email']
        city = form_data['city']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE employees SET name=%s, email=%s, city=%s WHERE id=%s",
                    (name, email, city, emp_id))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def delete_employee(emp_id):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM employees WHERE id=%s", (emp_id,))
        mysql.connection.commit()
        cur.close()
