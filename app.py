import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
app = Flask(__name__)

# --- ΡΥΘΜΙΣΗ ΒΑΣΗΣ ΔΕΔΟΜΕΝΩΝ ---
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            service TEXT,
            message TEXT,
            notes TEXT DEFAULT '', -- Για τις ενέργειες του διαχειριστή
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/company')
def company():
    return render_template('company.html')

@app.route('/services')
def services():
    return render_template('Services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/quote/<service>')
def get_quote(service):
    return render_template('quote_form.html', service=service)

@app.route('/sendData', methods=['POST'])
def send_data():
    name = request.form.get('Name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    # Εδώ γίνεται ο διαχωρισμός:
    # Αν υπάρχει το 'service_interest' το παίρνει, αλλιώς βάζει 'Γενική Επικοινωνία'
    service = request.form.get('service_interest', 'Γενική Επικοινωνία')
    comments = request.form.get('comments')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO leads (name, email, phone, service, message)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, email, phone, service, comments))
    conn.commit()
    conn.close()

    return render_template('success.html', name=name, email=email)

# ΠΕΡΙΟΧΗ ΔΙΑΧΕΙΡΙΣΤΗ (Εδώ θα βλέπεις τα πάντα)
@app.route('/admin/dashboard')
def admin_dashboard():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM leads ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    return render_template('admin.html', leads=rows)


# 2. Διαγραφή Πελάτη
@app.route('/admin/delete/<int:id>')
def delete_lead(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM leads WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))


# 3. Σελίδα Επεξεργασίας (Φόρμα για Notes)
@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
def edit_lead(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        new_entry = request.form.get('new_note')
        current_notes = request.form.get('old_notes')  # Οι παλιές σημειώσεις

        if new_entry.strip():  # Αν ο διαχειριστής έγραψε κάτι
            timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
            # Προσθήκη της νέας ενέργειας πάνω από τις παλιές (Append με ημερομηνία)
            updated_notes = f"[{timestamp}]: {new_entry}\n{current_notes}"

            cursor.execute('UPDATE leads SET notes = ? WHERE id = ?', (updated_notes, id))
            conn.commit()

        conn.close()
        return redirect(url_for('admin_dashboard'))

    cursor.execute('SELECT * FROM leads WHERE id = ?', (id,))
    lead = cursor.fetchone()
    conn.close()
    return render_template('edit_lead.html', lead=lead)
if __name__ == '__main__':
    app.run(debug=True)