from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
import bcrypt

app = Flask(__name__)
CORS(app)

# MySQL connection setup
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='root123',  # Apna password daalo
    database='dsa_learning',
    port=3307  # Apna port daalo
)

@app.route('/')
def home():
    return "Hello, Flask is working!"

# API to get all topics
@app.route('/api/topics', methods=['GET'])
def get_topics():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM topics")
    topics = cursor.fetchall()
    topics_list = [{'id': topic[0], 'name': topic[1]} for topic in topics]
    return jsonify(topics_list)

# API to get problems for a specific topic
@app.route('/api/problems/<int:topic_id>', methods=['GET'])
def get_problems(topic_id):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM problems WHERE topic_id = %s", (topic_id,))
    problems = cursor.fetchall()
    problems_list = [{'id': problem[0], 'topic_id': problem[1], 'title': problem[2], 'description': problem[3]} for problem in problems]
    return jsonify(problems_list)

# API to signup
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data['username']
    password = data['password'].encode('utf-8')

    # Hash the password
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )
        connection.commit()
        return jsonify({"message": "User created successfully"})
    except pymysql.err.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400

# API to login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password'].encode('utf-8')

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password, user[2].encode('utf-8')):
        return jsonify({"message": "Login successful", "user_id": user[0]})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# API to get user progress
@app.route('/api/user-progress/<int:user_id>', methods=['GET'])
def get_user_progress(user_id):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT p.id, p.title, p.description, up.solved FROM problems p LEFT JOIN user_progress up ON p.id = up.problem_id AND up.user_id = %s WHERE up.solved = 1",
        (user_id,)
    )
    progress = cursor.fetchall()
    progress_list = [{'id': item[0], 'title': item[1], 'description': item[2], 'solved': item[3]} for item in progress]
    return jsonify(progress_list)

# API to update user progress (mark problem as solved)
@app.route('/api/user-progress', methods=['POST'])
def update_progress():
    data = request.get_json()
    user_id = data['user_id']
    problem_id = data['problem_id']
    solved = data['solved']

    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO user_progress (user_id, problem_id, solved) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE solved = %s",
        (user_id, problem_id, solved, solved)
    )
    connection.commit()
    return jsonify({"message": "Progress updated successfully"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)