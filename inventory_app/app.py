from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import qrcode
import os
import uuid

app = Flask(__name__)

# === Configuration ===
DB = 'inventory.db'
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB upload limit
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# === Utility: Check valid file type ===
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# === Ensure folders exist ===
os.makedirs('static/qrcodes', exist_ok=True)
os.makedirs('static/images', exist_ok=True)

# === Initialize SQLite database if not present ===
def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT,
                name TEXT,
                location TEXT,
                description TEXT,
                in_stock BOOLEAN,
                tags TEXT,
                image TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        ''')

# === Homepage: List all tools ===
@app.route('/')
def index():
    with sqlite3.connect(DB) as conn:
        tools = conn.execute("SELECT * FROM tools").fetchall()
    return render_template('index.html', tools=tools)

# === Add new tool ===
@app.route('/add', methods=['GET', 'POST'])
def add_tool():
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        saved_locations = cursor.execute("SELECT name FROM locations ORDER BY name").fetchall()

    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location'].strip()
        tags = request.form.get('tags', '')
        description = "N/A"
        in_stock = 1
        tool_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, name + str(uuid.uuid1())))[:8]

        # ✅ Handle image upload
        image_file = request.files.get('image')
        image_filename = None
        if image_file and allowed_file(image_file.filename):
            ext = image_file.filename.rsplit('.', 1)[1].lower()
            image_filename = f"{tool_uuid}.{ext}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)

        # ✅ Save tool to DB
        with sqlite3.connect(DB) as conn:
            cur = conn.cursor()
            cur.execute("INSERT OR IGNORE INTO locations (name) VALUES (?)", (location,))
            cur.execute("""
                INSERT INTO tools (uuid, name, location, description, in_stock, tags, image)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tool_uuid, name, location, description, in_stock, tags, image_filename))
            tool_id = cur.lastrowid
            conn.commit()

        # ✅ Generate local QR Code (defaulting to localhost access)
        tool_url = url_for('tool_detail', tool_id=tool_id, _external=True)
        img = qrcode.make(tool_url)
        img.save(f'static/qrcodes/{tool_id}.png')

        return redirect(url_for('index'))

    return render_template('add_tool.html', locations=[loc[0] for loc in saved_locations])

# === Tool Detail Page ===
@app.route('/tool/<int:tool_id>')
def tool_detail(tool_id):
    with sqlite3.connect(DB) as conn:
        tool = conn.execute("SELECT * FROM tools WHERE id=?", (tool_id,)).fetchone()
    return render_template('tool_detail.html', tool=tool)

# === Edit Tool Page ===
@app.route('/tool/<int:tool_id>/edit', methods=['GET', 'POST'])
def edit_tool(tool_id):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        tool = cursor.execute("SELECT * FROM tools WHERE id=?", (tool_id,)).fetchone()

        if request.method == 'POST':
            name = request.form['name']
            location = request.form['location']
            description = request.form['description']
            tags = request.form['tags']
            in_stock = int(request.form.get('in_stock', 0))

            cursor.execute("""
                UPDATE tools SET name=?, location=?, description=?, tags=?, in_stock=? WHERE id=?
            """, (name, location, description, tags, in_stock, tool_id))
            conn.commit()
            return redirect(url_for('tool_detail', tool_id=tool_id))

    return render_template('edit_tool.html', tool=tool)

# === Delete Tool Handler ===
@app.route('/tool/<int:tool_id>/delete', methods=['POST'])
def delete_tool(tool_id):
    with sqlite3.connect(DB) as conn:
        conn.execute("DELETE FROM tools WHERE id=?", (tool_id,))
        conn.commit()
    return redirect(url_for('index'))

# === Run the app locally ===
if __name__ == '__main__':
    init_db()
    app.run(debug=True)

