from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'

# MySQL Configuration Function
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='passWord@11', 
        database='task_manager_db'
    )

# --- ROUTES ---

# 1. Login Page Route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM manager_login WHERE username = %s AND password = %s", (username, password))
        manager = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if manager:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid ID or Password")
            
    return render_template('login.html')

# 2. Dashboard Route (Protected)
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('dashboard.html', tasks=tasks)

# 3. Add Task API
@app.route('/add_task', methods=['POST'])
def add_task():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    title = request.form.get('title')
    if title:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (title, status) VALUES (%s, 'Pending')", (title,))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for('dashboard'))

# 4. Update Task Status API
@app.route('/update_task/<int:task_id>', methods=['POST'])
def update_task(task_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    status = request.form.get('status')
    if status in ['Pending', 'Completed']:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (status, task_id))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for('dashboard'))

# 5. Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)