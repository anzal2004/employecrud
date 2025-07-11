from extensions import mysql
from datetime import date, datetime

class AttendanceModel:

    @staticmethod
    def mark_attendance(employee_id):
        today = date.today()
        now_time = datetime.now().time()

        cur = mysql.connection.cursor()

        # Check today's attendance
        cur.execute("SELECT * FROM attendance WHERE employee_id=%s AND date=%s", (employee_id, today))
        record = cur.fetchone()

        if not record:
            # Sign In
            cur.execute("""
                INSERT INTO attendance (employee_id, date, sign_in, sign_out)
                VALUES (%s, %s, %s, %s)
            """, (employee_id, today, now_time, None))
            mysql.connection.commit()
            status = "Signed In"
        elif record and record[4] is None:
            # Sign Out
            cur.execute("""
                UPDATE attendance SET sign_out=%s WHERE id=%s
            """, (now_time, record[0]))
            mysql.connection.commit()
            status = "Signed Out"
        else:
            status = "Already Signed Out Today"

        cur.close()
        return {"status": status, "time": now_time.strftime('%H:%M:%S')}

    @staticmethod
    def today_summary():
        today = date.today()
        cur = mysql.connection.cursor()

        # Total present today
        cur.execute("""
            SELECT COUNT(DISTINCT employee_id)
            FROM attendance
            WHERE date=%s
        """, (today,))
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

        return {
            "present": present_count,
            "absent": absent_count,
            "records": records
        }

    @staticmethod
    def today_attendance():
        """Fetch only today's attendance records."""
        today = date.today()
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT e.name, a.date, a.sign_in, a.sign_out
            FROM attendance a
            JOIN employees e ON a.employee_id = e.id
            WHERE a.date = %s
            ORDER BY a.sign_in
        """, (today,))
        records = cur.fetchall()
        cur.close()
        return records

    @staticmethod
    def all_attendance():
        """Fetch all attendance records."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT e.name, a.date, a.sign_in, a.sign_out
            FROM attendance a
            JOIN employees e ON a.employee_id = e.id
            ORDER BY a.date DESC
        """)
        records = cur.fetchall()
        cur.close()
        return records
