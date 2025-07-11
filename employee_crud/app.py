# app.py

from flask import Flask, render_template, request, jsonify
from extensions import mysql
from routes.auth_routes import auth_bp
from routes.employee_routes import employee_bp
from routes.attendance_routes import attendance_bp
from routes.report_routes import report_bp

# ✅ Import your chatbot logic
# Ensure chatbot.py exists in the same folder or adjust import accordingly.
try:
    from chatbot import handle_chatbot_query
except ModuleNotFoundError:
    handle_chatbot_query = None
    print("⚠️ chatbot.py module not found. Chatbot routes will not work until it is added.")

app = Flask(__name__)
app.config.from_pyfile('config.py')

# Initialize MySQL extension
mysql.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(employee_bp, url_prefix='/employee')
app.register_blueprint(attendance_bp, url_prefix='/attendance')
app.register_blueprint(report_bp, url_prefix='/reports')

# ✅ Chatbot API route
@app.route('/chatbot', methods=['POST'])
def chatbot_api():
    if handle_chatbot_query is None:
        return jsonify({'response': 'Chatbot module not available.'}), 500

    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({'response': 'No question provided.'}), 400
    response = handle_chatbot_query(question)
    return jsonify({'response': response})

# ✅ Chatbot page route
@app.route('/chat')
def chat_page():
    return render_template('chatbot.html')

if __name__ == '__main__':
    app.run(debug=True)
