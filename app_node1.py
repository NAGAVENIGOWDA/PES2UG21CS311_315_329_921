



from flask import Flask, render_template, request, jsonify
import mysql.connector
import threading
from raft_node import RaftNode  # Import the RaftNode class
from flask import jsonify
app = Flask(__name__)

# Connect to the MySQL database
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",
    database="task_management"
)
db_cursor = db_connection.cursor()

# Raft node initialization
raft_node = RaftNode(node_id=1, peers=[2, 3], flask_url="http://localhost:5000")
raft_node.start()  # Start the Raft node

# Routes for task management
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if request.method == 'GET':
        # Retrieve tasks from the database
        db_cursor.execute("SELECT * FROM tasks")
        tasks = db_cursor.fetchall()
        # Convert task data to dictionary format
        tasks_dict = [{'id': task[0], 'title': task[1], 'description': task[2], 'status': task[3]} for task in tasks]
        return jsonify(tasks_dict)
    elif request.method == 'POST':
        task_data = request.json
        # Add task to the database
        db_cursor.execute("INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s)", (task_data['title'], task_data['description'], task_data['status']))
        db_connection.commit()
        # Retrieve the added task from the database
        db_cursor.execute("SELECT * FROM tasks WHERE id = LAST_INSERT_ID()")
        added_task = db_cursor.fetchone()
        # Convert added task data to dictionary format
        added_task_dict = {'id': added_task[0], 'title': added_task[1], 'description': added_task[2], 'status': added_task[3]}
        return jsonify({"message": "Task added successfully", "task": added_task_dict}), 201

@app.route('/tasks/<int:task_id>', methods=['PATCH', 'DELETE'])
def update_or_delete_task(task_id):
    if request.method == 'PATCH':
        updated_data = request.json
        # Check which fields are present in the request and update only those fields
        if 'title' in updated_data:
            db_cursor.execute("UPDATE tasks SET title = %s WHERE id = %s", (updated_data['title'], task_id))
        if 'description' in updated_data:
            db_cursor.execute("UPDATE tasks SET description = %s WHERE id = %s", (updated_data['description'], task_id))
        if 'status' in updated_data:
            db_cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (updated_data['status'], task_id))
        db_connection.commit()
        return jsonify({"message": "Task updated successfully"})

    elif request.method == 'DELETE':
        # Delete task from the database
        db_cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        db_connection.commit()
        return jsonify({"message": "Task deleted successfully"})



# Variables to keep track of current term and who we voted for
current_term = 0
voted_for = None

@app.route('/request_vote', methods=['POST'])
def request_vote():
    global current_term, voted_for

    data = request.json
    term = data.get('term')
    candidate_id = data.get('candidate_id')
    last_log_index = data.get('last_log_index')
    last_log_term = data.get('last_log_term')

    # Implement Raft voting logic here
    if term > current_term and (voted_for is None or voted_for == candidate_id):
        current_term = term
        voted_for = candidate_id
        vote_granted = True
    else:
        vote_granted = False

    return jsonify({'vote_granted': vote_granted})

if __name__ == '__main__':
    app.run(debug=True)

