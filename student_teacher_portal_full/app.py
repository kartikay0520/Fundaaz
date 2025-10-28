from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import csv, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

STUDENT_FILE = 'students.csv'
TEACHER_FILE = 'teachers.csv'
TEST_FILE = 'tests.csv'
SPECIAL_KEY = 'TEACHER123'  # Special teacher login key

# Ensure CSVs exist
for file, headers in [
    (STUDENT_FILE, ['name','password','class','phone1','phone2','phone3']),
    (TEACHER_FILE, ['name','password']),
    (TEST_FILE, ['student','class','subject','test_no','marks','total_marks','date'])
]:
    if not os.path.exists(file):
        with open(file,'w',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        role = request.form['role']

        if not name or not password:
            flash('Please enter both name and password.', 'error')
            return render_template('login.html')

        if role == 'student':
            with open(STUDENT_FILE) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['name'] == name and row['password'] == password:
                        session['user'] = name
                        session['role'] = 'student'
                        flash('Login successful!', 'success')
                        return redirect(url_for('student_dashboard'))
            flash('Invalid student credentials.', 'error')

        elif role == 'teacher':
            key = request.form.get('key','')
            if key != SPECIAL_KEY:
                flash('Invalid teacher key.', 'error')
                return render_template('login.html')
            with open(TEACHER_FILE) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['name'] == name and row['password'] == password:
                        session['user'] = name
                        session['role'] = 'teacher'
                        flash('Login successful!', 'success')
                        return redirect(url_for('teacher_dashboard'))
            flash('Invalid teacher credentials.', 'error')

    return render_template('login.html')

@app.route('/register_teacher', methods=['GET','POST'])
def register_teacher():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        key = request.form['key']

        if not name or not password:
            flash('Please enter both name and password.', 'error')
            return render_template('register_teacher.html')

        if key != SPECIAL_KEY:
            flash('Invalid teacher key.', 'error')
            return render_template('register_teacher.html')

        with open(TEACHER_FILE) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['name'] == name:
                    flash('Teacher already exists.', 'error')
                    return render_template('register_teacher.html')

        with open(TEACHER_FILE,'a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow([name,password])

        flash('Teacher registered successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('register_teacher.html')

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if session.get('role') != 'teacher':
        flash('Please login as a teacher.', 'error')
        return redirect(url_for('login'))

    tests = []
    with open(TEST_FILE) as f:
        reader = csv.DictReader(f)
        tests = list(reader)

    students = []
    with open(STUDENT_FILE) as f:
        reader = csv.DictReader(f)
        students = list(reader)

    total_students = len(students)
    total_tests = len(tests)
    avg_percentage = 0
    percentages = []
    for t in tests:
        try:
            percent = (float(t['marks'])/float(t['total_marks']))*100 if float(t['total_marks']) > 0 else 0
            percentages.append(percent)
        except:
            pass
    if percentages:
        avg_percentage = round(sum(percentages)/len(percentages),2)

    return render_template('teacher_dashboard.html', tests=tests, students=students,
                           total_students=total_students, total_tests=total_tests, avg_percentage=avg_percentage)

@app.route('/student_dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        flash('Please login as a student.', 'error')
        return redirect(url_for('login'))

    student = session.get('user')
    student_info = {}
    tests = []

    with open(STUDENT_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['name'] == student:
                student_info = row
                break

    with open(TEST_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['student'] == student:
                row['percentage'] = round((float(row['marks'])/float(row['total_marks'])*100) if float(row['total_marks']) > 0 else 0,2)
                tests.append(row)

    total_tests = len(tests)
    avg_percentage = round(sum([t['percentage'] for t in tests])/total_tests,2) if total_tests else 0

    return render_template('student_dashboard.html', name=student, info=student_info, tests=tests,
                           total_tests=total_tests, avg_percentage=avg_percentage)

@app.route('/add_student', methods=['POST'])
def add_student():
    if session.get('role') != 'teacher':
        flash('Please login as a teacher.', 'error')
        return redirect(url_for('login'))

    name = request.form['name']
    password = request.form['password']
    student_class = request.form['class']
    phone1 = request.form['phone1']
    phone2 = request.form['phone2']
    phone3 = request.form['phone3']

    valid_numbers = [num for num in [phone1, phone2, phone3] if num.isdigit() and len(num)==10]
    if len(valid_numbers) < 1:
        flash("At least one valid 10-digit phone number required.", 'error')
        return redirect(url_for('teacher_dashboard'))

    with open(STUDENT_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['name'] == name:
                flash("Student already exists.", 'error')
                return redirect(url_for('teacher_dashboard'))

    with open(STUDENT_FILE,'a',newline='') as f:
        writer = csv.writer(f)
        writer.writerow([name,password,student_class,phone1,phone2,phone3])

    flash("Student added successfully!", 'success')
    return redirect(url_for('teacher_dashboard'))

@app.route('/add_test', methods=['POST'])
def add_test():
    if session.get('role') != 'teacher':
        flash('Please login as a teacher.', 'error')
        return redirect(url_for('login'))

    student = request.form['student']
    student_class = request.form['class']
    subject = request.form['subject']
    test_no = request.form['test_no']
    marks = request.form['marks']
    total_marks = request.form['total_marks']
    date = request.form['date'] or datetime.now().strftime('%Y-%m-%d')

    if not student or not subject or not test_no or not marks or not total_marks:
        flash('Please fill all test fields.', 'error')
        return redirect(url_for('teacher_dashboard'))

    try:
        marks = float(marks)
        total_marks = float(total_marks)
        if marks < 0 or total_marks <= 0 or marks > total_marks:
            flash('Invalid marks entered.', 'error')
            return redirect(url_for('teacher_dashboard'))
    except:
        flash('Marks must be numbers.', 'error')
        return redirect(url_for('teacher_dashboard'))

    with open(TEST_FILE,'a',newline='') as f:
        writer = csv.writer(f)
        writer.writerow([student, student_class, subject, test_no, marks, total_marks, date])

    flash('Test added successfully!', 'success')
    return redirect(url_for('teacher_dashboard'))

@app.route('/get_progress')
def get_progress():
    student = request.args.get('student')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    results = []
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except:
        return jsonify([])

    with open(TEST_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['student'] == student:
                try:
                    test_dt = datetime.strptime(row['date'], "%Y-%m-%d")
                except:
                    continue
                if start_dt <= test_dt <= end_dt:
                    percentage = round((float(row['marks'])/float(row['total_marks'])*100) if float(row['total_marks']) > 0 else 0,2)
                    results.append({
                        'subject': row['subject'],
                        'test_no': row['test_no'],
                        'marks': row['marks'],
                        'total_marks': row['total_marks'],
                        'date': row['date'],
                        'percentage': percentage
                    })
    results.sort(key=lambda x: x['date'])
    return jsonify(results)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

if __name__=='__main__':
    app.run(debug=True)