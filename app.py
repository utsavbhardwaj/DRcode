from flask import Flask, render_template, request, redirect, session, send_file, url_for
import sqlite3, csv, io, os, math
from datetime import datetime
from fpdf import FPDF
import tempfile

app = Flask(__name__)
app.secret_key = 'your_secret_key'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password123'
DB_PATH = "database.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS orientation_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                designation TEXT,
                dob TEXT,
                drdo_joining TEXT,
                sspl_joining TEXT,
                service TEXT,
                address TEXT,
                email TEXT,
                mobile TEXT,
                education TEXT,
                field TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        ''')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'designation': request.form['designation'],
            'dob': request.form['dob'],
            'drdo_joining': request.form.get('drdo_joining', ''),
            'sspl_joining': request.form.get('sspl_joining', ''),
            'service': request.form.get('service', ''),
            'address': request.form.get('address', ''),
            'email': request.form.get('email', ''),
            'mobile': request.form.get('mobile', ''),
            'education': request.form.get('education', ''),
            'field': request.form.get('field', '')
        }

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO orientation_entries 
                (name, designation, dob, drdo_joining, sspl_joining, service, address, email, mobile, education, field)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(data.values()))
            entry_id = c.lastrowid
            conn.commit()

        return redirect(url_for('thank_you', entry_id=entry_id))

    return render_template('form.html')

@app.route('/thank-you')
def thank_you():
    entry_id = request.args.get('entry_id')
    return render_template('thank_you.html', entry_id=entry_id)

import tempfile

import tempfile

@app.route('/download_pdf/<int:entry_id>')
def download_pdf(entry_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orientation_entries WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        if not row:
            return "Entry not found", 404
        headers = [desc[0] for desc in cursor.description]

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_title("Orientation Entry")

    pdf.cell(200, 10, txt="Orientation Entry Summary", ln=True, align='C')
    pdf.ln(10)

    for key, value in zip(headers, row):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, f"{key.replace('_',' ').title()}: ", ln=False)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, str(value))

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp:
        pdf.output(temp.name)
        temp_path = temp.name

    return send_file(temp_path, as_attachment=True, download_name=f'orientation_entry_{entry_id}.pdf')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect('/admin')
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect('/login')

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect('/login')

    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        total_count = cursor.execute("SELECT COUNT(*) FROM orientation_entries").fetchone()[0]
        total_pages = math.ceil(total_count / per_page)
        cursor.execute("SELECT * FROM orientation_entries ORDER BY id DESC LIMIT ? OFFSET ?", (per_page, offset))
        entries = cursor.fetchall()
        latest = cursor.execute("SELECT MAX(timestamp) FROM orientation_entries").fetchone()[0]

    return render_template('admin.html', entries=entries, page=page, total_pages=total_pages,
                           total_count=total_count, latest=latest)

@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    if not session.get('admin_logged_in'):
        return redirect('/login')
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM orientation_entries WHERE id = ?", (entry_id,))
        conn.commit()
    return redirect('/admin')

@app.route('/export/csv')
def export_csv():
    if not session.get('admin_logged_in'):
        return redirect('/login')

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT * FROM orientation_entries")
        entries = cursor.fetchall()
        headers = [desc[0] for desc in cursor.description]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(entries)
    output.seek(0)

    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv',
                     download_name="orientation_entries.csv", as_attachment=True)

@app.route('/sw.js')
def service_worker():
    return app.send_static_file('sw.js')

if __name__ == '__main__':
    init_db()
    # Try using adhoc SSL for LAN PWA support
    try:
        app.run(host="0.0.0.0", port=5003, debug=False, ssl_context='adhoc')
    except Exception as e:
        print(f"Running without HTTPS (LAN PWA might not work): {e}")
        app.run(host="0.0.0.0", port=5003, debug=False)

