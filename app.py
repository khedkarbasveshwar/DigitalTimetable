from flask import Flask, render_template, request, redirect
import pymysql

app = Flask(__name__)

# ---------------- Database Connection ----------------
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",  # XAMPP default has no password
        database="cse_timetable_db"
    )

# ---------------- Home Route ----------------
@app.route('/')
def home():
    return render_template("index.html")

# ---------------- Login Route ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM admin WHERE username=%s AND password=%s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        conn.close()

        if result:
            return redirect("/dashboard")
        else:
            return "<h2>Invalid Credentials</h2>"

    return render_template("login.html")

# ---------------- Dashboard Route ----------------
@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

# ---------------- Add Faculty ----------------
@app.route('/add_faculty', methods=['GET', 'POST'])
def add_faculty():
    if request.method == 'POST':
        faculty_id = request.form['faculty_id']
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        subject = request.form['subject']
        designation = request.form['designation']

        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO faculty (faculty_id, name, email, subject, designation, mobile)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (faculty_id, name, email, subject, designation, mobile))
        conn.commit()
        conn.close()
        return redirect("/view_faculty")

    return render_template("add_faculty.html")

# ---------------- View Faculty ----------------
@app.route('/view_faculty')
def view_faculty():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faculty")
    faculty = cursor.fetchall()
    conn.close()
    return render_template("view_faculty.html", faculty=faculty)

# ---------------- Edit Faculty ----------------
@app.route('/edit_faculty/<string:faculty_id>', methods=['GET', 'POST'])
def edit_faculty(faculty_id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        subject = request.form['subject']
        designation = request.form['designation']

        query = """
            UPDATE faculty 
            SET name=%s, email=%s, subject=%s, designation=%s, mobile=%s
            WHERE faculty_id=%s
        """
        cursor.execute(query, (name, email, subject, designation, mobile, faculty_id))
        conn.commit()
        conn.close()
        return redirect("/view_faculty")

    cursor.execute("SELECT * FROM faculty WHERE faculty_id=%s", (faculty_id,))
    faculty = cursor.fetchone()
    conn.close()
    return render_template("edit_faculty.html", faculty=faculty)

# ---------------- Delete Faculty ----------------
@app.route('/delete_faculty/<string:faculty_id>')
def delete_faculty(faculty_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faculty WHERE faculty_id=%s", (faculty_id,))
    conn.commit()
    conn.close()
    return redirect("/view_faculty")

# ---------------- Generate Timetable ----------------
@app.route('/generate_timetable', methods=['GET', 'POST'])
def generate_timetable():
    conn = get_connection()
    cursor = conn.cursor()

    # Dropdown options
    years = ['FY', 'SY', 'TY']
    cursor.execute("SELECT faculty_id, name FROM faculty")
    faculty_list = cursor.fetchall()
    cursor.execute("SELECT DISTINCT room FROM timetable")
    rooms = [r[0] for r in cursor.fetchall()]

    timetable_data = []

    if request.method == 'POST':
        selected_year = request.form.get('year')
        selected_faculty = request.form.get('faculty')
        selected_room = request.form.get('room')

        query = "SELECT day, subject, faculty_id, room, time_slot FROM timetable WHERE 1=1"
        params = []

        if selected_year:
            query += " AND year=%s"
            params.append(selected_year)
        if selected_faculty:
            query += " AND faculty_id=%s"
            params.append(selected_faculty)
        if selected_room:
            query += " AND room=%s"
            params.append(selected_room)

        query += " ORDER BY FIELD(day,'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'), time_slot"
        cursor.execute(query, tuple(params))
        timetable_data = cursor.fetchall()

    conn.close()
    return render_template('generate_timetable.html',
                           years=years,
                           faculty_list=faculty_list,
                           rooms=rooms,
                           timetable=timetable_data)

# ---------------- Main ----------------
if __name__ == '__main__':
    app.run(debug=True)