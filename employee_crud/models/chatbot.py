# chatbot.py

import spacy
import pymysql
from extensions import get_connection  # use your existing DB connection

nlp = spacy.load("en_core_web_sm")

def handle_chatbot_query(question):
    question = question.lower()

    if "present today" in question or "attendance today" in question:
        query = "SELECT COUNT(*) as count FROM attendance WHERE date = CURDATE() AND status = 'Present';"
        return run_query(query, "Employees present today: ")

    elif "male" in question and "female" in question:
        query = "SELECT gender, COUNT(*) as count FROM employees GROUP BY gender;"
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                response = ""
                for row in rows:
                    response += f"{row['gender']}: {row['count']} employees\n"
                return response.strip()

    elif "total employees" in question:
        query = "SELECT COUNT(*) as count FROM employees;"
        return run_query(query, "Total employees: ")

    else:
        return "Sorry, I didn't understand your question. Please ask differently."

def run_query(query, prefix):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchone()
            return f"{prefix}{row['count']}"
