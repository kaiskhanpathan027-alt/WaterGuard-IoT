"""
Database management module for Water Quality Monitoring System.
Handles SQLite database initialization, automated migrations, user auth records,
custom username generation (firstname.lastname@water.guard), and persistent test history.
"""

import sqlite3
import os
import re
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from water_quality import analyze_water_sample

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "water_quality.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def generate_custom_username(first_name, last_name, conn=None):
    """
    Generates an application custom username in the format: firstname.lastname@water.guard
    - Automatically convert to lowercase
    - Remove unnecessary spaces and special characters
    - Ensure every username is unique; if conflict exists, append an incremental number
    """
    fn = re.sub(r'[^a-zA-Z0-9]', '', (first_name or '').strip().lower())
    ln = re.sub(r'[^a-zA-Z0-9]', '', (last_name or '').strip().lower())

    if not fn and not ln:
        fn, ln = "user", "water"
    elif not fn:
        fn = "user"
    elif not ln:
        ln = "analyst"

    base = f"{fn}.{ln}"
    domain = "@water.guard"
    candidate = f"{base}{domain}"

    should_close = False
    if conn is None:
        conn = get_db()
        should_close = True

    cursor = conn.cursor()
    counter = 1
    while True:
        cursor.execute("""
            SELECT id FROM users 
            WHERE LOWER(custom_username) = LOWER(?) OR LOWER(username) = LOWER(?)
        """, (candidate, candidate))
        if not cursor.fetchone():
            break
        candidate = f"{base}{counter}{domain}"
        counter += 1

    if should_close:
        conn.close()

    return candidate

def init_db():
    """
    Initializes tables, performs safe schema migrations (adding custom_username, first_name, last_name),
    and ensures persistent seed data without deleting existing records.
    """
    conn = get_db()
    cursor = conn.cursor()

    # 1. Base Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            full_name TEXT,
            first_name TEXT,
            last_name TEXT,
            custom_username TEXT UNIQUE,
            college_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Base Tests Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sample_name TEXT NOT NULL,
            location TEXT NOT NULL,
            source_type TEXT NOT NULL,
            ph REAL NOT NULL,
            tds REAL NOT NULL,
            turbidity REAL NOT NULL,
            wqi_score REAL NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            tested_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
    """)
    conn.commit()

    # 3. Safe Schema Migration Check
    cursor.execute("PRAGMA table_info(users)")
    existing_cols = [row[1] for row in cursor.fetchall()]

    if 'first_name' not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN first_name TEXT;")
    if 'last_name' not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN last_name TEXT;")
    if 'custom_username' not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN custom_username TEXT;")
    conn.commit()

    # 4. Backfill custom_username for existing users if null
    cursor.execute("SELECT id, username, full_name, custom_username FROM users WHERE custom_username IS NULL OR custom_username = ''")
    unmigrated = cursor.fetchall()
    for row in unmigrated:
        full = (row['full_name'] or row['username'] or 'User Analyst').strip()
        parts = full.split()
        fn = parts[0] if parts else 'user'
        ln = parts[-1] if len(parts) > 1 else 'analyst'
        new_uname = generate_custom_username(fn, ln, conn=conn)
        cursor.execute("UPDATE users SET first_name = ?, last_name = ?, custom_username = ? WHERE id = ?", (fn, ln, new_uname, row['id']))
    conn.commit()

    # 5. Ensure Core Demonstration Accounts Exist
    # Admin Account
    cursor.execute("SELECT id FROM users WHERE email = ? OR custom_username = ?", ("admin@waterguard.edu", "admin.director@water.guard"))
    admin_row = cursor.fetchone()
    if not admin_row:
        admin_pass = generate_password_hash("admin123")
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, full_name, first_name, last_name, custom_username, college_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "admin.director@water.guard",
            "admin@waterguard.edu",
            admin_pass,
            "admin",
            "Dr. Admin Lab Director",
            "Admin",
            "Director",
            "admin.director@water.guard",
            "MIT-ADMIN-01"
        ))
        admin_id = cursor.lastrowid
    else:
        admin_id = admin_row[0]

    # Demo Student: Alex Turner
    cursor.execute("SELECT id FROM users WHERE email = ? OR custom_username = ?", ("student@college.edu", "alex.turner@water.guard"))
    student_row = cursor.fetchone()
    if not student_row:
        student_pass = generate_password_hash("student123")
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, full_name, first_name, last_name, custom_username, college_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "alex.turner@water.guard",
            "student@college.edu",
            student_pass,
            "user",
            "Alex Turner",
            "Alex",
            "Turner",
            "alex.turner@water.guard",
            "MIT-CSD-2026-01"
        ))
        student_id = cursor.lastrowid
    else:
        student_id = student_row[0]

    # Project Creator 1: Kais Khan Fakirmat Khan
    cursor.execute("SELECT id FROM users WHERE custom_username = ?", ("kais.khan@water.guard",))
    kais_row = cursor.fetchone()
    if not kais_row:
        kais_pass = generate_password_hash("kais123")
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, full_name, first_name, last_name, custom_username, college_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "kais.khan@water.guard",
            "kais.khan@mit.edu",
            kais_pass,
            "user",
            "Kais Khan Fakirmat Khan",
            "Kais",
            "Khan",
            "kais.khan@water.guard",
            "MIT-CSD-2026-KK"
        ))
        kais_id = cursor.lastrowid
    else:
        kais_id = kais_row[0]

    # Project Creator 2: Rajeshwar Sandip Gaurkar
    cursor.execute("SELECT id FROM users WHERE custom_username = ?", ("rajeshwar.gaurkar@water.guard",))
    raj_row = cursor.fetchone()
    if not raj_row:
        raj_pass = generate_password_hash("rajeshwar123")
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, full_name, first_name, last_name, custom_username, college_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "rajeshwar.gaurkar@water.guard",
            "rajeshwar.gaurkar@mit.edu",
            raj_pass,
            "user",
            "Rajeshwar Sandip Gaurkar",
            "Rajeshwar",
            "Gaurkar",
            "rajeshwar.gaurkar@water.guard",
            "MIT-CSD-2026-RG"
        ))
        raj_id = cursor.lastrowid
    else:
        raj_id = raj_row[0]

    conn.commit()

    # 6. Seed sample tests if tests table is empty
    cursor.execute("SELECT COUNT(*) FROM tests")
    if cursor.fetchone()[0] == 0:
        seed_samples = [
            {
                "sample_name": "Main Academic Block Water Cooler",
                "location": "Academic Block A - 2nd Floor",
                "source_type": "RO Purified Tap",
                "ph": 7.3,
                "tds": 142.0,
                "turbidity": 0.45,
                "notes": "Post-filtration output from multi-stage commercial RO unit.",
                "days_ago": 12,
                "user_id": student_id,
                "tested_by": "Alex Turner"
            },
            {
                "sample_name": "Hostel 3 Borewell Intake",
                "location": "Boys Hostel 3 Pump House",
                "source_type": "Groundwater / Borewell",
                "ph": 8.6,
                "tds": 680.0,
                "turbidity": 6.8,
                "notes": "Slight turbidity noted after heavy rainfall; elevated TDS mineral hardness.",
                "days_ago": 9,
                "user_id": student_id,
                "tested_by": "Alex Turner"
            },
            {
                "sample_name": "Campus Canteen Kitchen Supply",
                "location": "Central Dining Hall Kitchen",
                "source_type": "Municipal Tap",
                "ph": 7.1,
                "tds": 260.0,
                "turbidity": 1.2,
                "notes": "Complies with drinking standards. Tested prior to lunch prep.",
                "days_ago": 7,
                "user_id": kais_id,
                "tested_by": "Kais Khan Fakirmat Khan"
            },
            {
                "sample_name": "College Botanical Garden Pond",
                "location": "East Campus Botanical Area",
                "source_type": "Surface / Lake Water",
                "ph": 5.8,
                "tds": 980.0,
                "turbidity": 18.5,
                "notes": "High organic sediment and acidic runoff detected. Strictly unfit for drinking.",
                "days_ago": 5,
                "user_id": kais_id,
                "tested_by": "Kais Khan Fakirmat Khan"
            },
            {
                "sample_name": "Computer Science & Design Lab Tap",
                "location": "CSD Dept Lab 204",
                "source_type": "Tap Water",
                "ph": 7.4,
                "tds": 185.0,
                "turbidity": 0.8,
                "notes": "Reference baseline sample tested for sensor calibration.",
                "days_ago": 3,
                "user_id": raj_id,
                "tested_by": "Rajeshwar Sandip Gaurkar"
            },
            {
                "sample_name": "Sports Complex Water Point",
                "location": "Outdoor Stadium Pavilion",
                "source_type": "Overhead Tank Storage",
                "ph": 8.2,
                "tds": 520.0,
                "turbidity": 4.1,
                "notes": "Moderate mineral content; tank chlorination verified.",
                "days_ago": 2,
                "user_id": raj_id,
                "tested_by": "Rajeshwar Sandip Gaurkar"
            },
            {
                "sample_name": "Rainwater Harvesting Catchment",
                "location": "Library Terrace Cistern",
                "source_type": "Rainwater",
                "ph": 6.8,
                "tds": 85.0,
                "turbidity": 1.9,
                "notes": "Freshly collected rainwater; very soft, low mineral content.",
                "days_ago": 1,
                "user_id": student_id,
                "tested_by": "Alex Turner"
            },
            {
                "sample_name": "Campus Boundary Storm Canal",
                "location": "North Gate Drainage Channel",
                "source_type": "Surface Runoff",
                "ph": 9.3,
                "tds": 1340.0,
                "turbidity": 28.0,
                "notes": "Heavy runoff and high sediment load. High contamination risk.",
                "days_ago": 0,
                "user_id": admin_id,
                "tested_by": "Dr. Admin Lab Director"
            }
        ]

        now = datetime.now()
        for sample in seed_samples:
            analysis = analyze_water_sample(sample["ph"], sample["tds"], sample["turbidity"])
            test_time = (now - timedelta(days=sample["days_ago"], hours=sample["days_ago"] * 2)).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO tests (
                    user_id, sample_name, location, source_type, ph, tds, turbidity,
                    wqi_score, status, notes, tested_by, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sample["user_id"],
                sample["sample_name"],
                sample["location"],
                sample["source_type"],
                sample["ph"],
                sample["tds"],
                sample["turbidity"],
                analysis["wqi_score"],
                analysis["overall_status"],
                sample["notes"],
                sample["tested_by"],
                test_time
            ))
        conn.commit()

    conn.close()

def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def get_user_by_login_identifier(identifier):
    """
    Finds a user by custom_username (firstname.lastname@water.guard), email, or legacy username.
    """
    if not identifier:
        return None
    ident = identifier.strip().lower()
    conn = get_db()
    user = conn.execute("""
        SELECT * FROM users 
        WHERE LOWER(custom_username) = ? 
           OR LOWER(email) = ? 
           OR LOWER(username) = ?
    """, (ident, ident, ident)).fetchone()
    conn.close()
    return user

def get_user_by_email(email):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),)).fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (username.strip(),)).fetchone()
    conn.close()
    return user

def get_user_by_custom_username(custom_username):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE LOWER(custom_username) = LOWER(?)", (custom_username.strip(),)).fetchone()
    conn.close()
    return user

def create_user(first_name, last_name, email, password, college_id=None, role="user"):
    """
    Creates a new user, generating their unique custom_username: firstname.lastname@water.guard
    """
    fn = (first_name or '').strip()
    ln = (last_name or '').strip()
    full_name = f"{fn} {ln}".strip() or fn or "Student Analyst"
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if email is already registered
    cursor.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
    if cursor.fetchone():
        conn.close()
        return None, None, "An account with this email address already exists."

    # Automatically generate custom username
    custom_username = generate_custom_username(fn, ln, conn=conn)
    password_hash = generate_password_hash(password)

    try:
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, full_name, first_name, last_name, custom_username, college_id, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            custom_username,
            email.strip(),
            password_hash,
            full_name,
            fn,
            ln,
            custom_username,
            college_id.strip() if college_id else None,
            role
        ))
        conn.commit()
        user_id = cursor.lastrowid
        return user_id, custom_username, None
    except sqlite3.IntegrityError as e:
        return None, None, "Registration failed due to a database constraint."
    finally:
        conn.close()

def save_test(user_id, sample_name, location, source_type, ph, tds, turbidity, notes, tested_by):
    analysis = analyze_water_sample(ph, tds, turbidity)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tests (
            user_id, sample_name, location, source_type, ph, tds, turbidity,
            wqi_score, status, notes, tested_by, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        user_id, sample_name.strip(), location.strip(), source_type.strip(),
        float(ph), float(tds), float(turbidity),
        analysis["wqi_score"], analysis["overall_status"],
        notes.strip() if notes else None, tested_by.strip()
    ))
    conn.commit()
    test_id = cursor.lastrowid
    conn.close()
    return test_id, analysis

def get_test_by_id(test_id):
    conn = get_db()
    test = conn.execute("""
        SELECT t.*, u.username, u.custom_username, u.email, u.full_name as user_full_name, u.first_name, u.last_name, u.college_id
        FROM tests t
        JOIN users u ON t.user_id = u.id
        WHERE t.id = ?
    """, (test_id,)).fetchone()
    conn.close()
    return test

def get_user_tests(user_id, search=None, status_filter=None, date_filter=None, limit=None):
    """
    Retrieves previous water tests for a specific user with search and date/status filters.
    """
    conn = get_db()
    query = "SELECT * FROM tests WHERE user_id = ?"
    params = [user_id]

    if status_filter and status_filter.lower() != 'all':
        query += " AND status = ?"
        params.append(status_filter.capitalize())

    if search:
        query += " AND (sample_name LIKE ? OR location LIKE ? OR source_type LIKE ? OR notes LIKE ?)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param, search_param])

    if date_filter:
        query += " AND date(created_at) = date(?)"
        params.append(date_filter.strip())

    query += " ORDER BY created_at DESC"

    if limit:
        query += f" LIMIT {int(limit)}"

    tests = conn.execute(query, params).fetchall()
    conn.close()
    return tests

def get_all_tests(search=None, status_filter=None, date_filter=None, limit=None):
    conn = get_db()
    query = """
        SELECT t.*, u.username, u.custom_username, u.full_name as user_full_name
        FROM tests t
        JOIN users u ON t.user_id = u.id
        WHERE 1=1
    """
    params = []

    if status_filter and status_filter.lower() != 'all':
        query += " AND t.status = ?"
        params.append(status_filter.capitalize())

    if search:
        query += " AND (t.sample_name LIKE ? OR t.location LIKE ? OR t.source_type LIKE ? OR u.custom_username LIKE ? OR u.username LIKE ?)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param, search_param, search_param])

    if date_filter:
        query += " AND date(t.created_at) = date(?)"
        params.append(date_filter.strip())

    query += " ORDER BY t.created_at DESC"

    if limit:
        query += f" LIMIT {int(limit)}"

    tests = conn.execute(query, params).fetchall()
    conn.close()
    return tests

def delete_test(test_id, user_id=None, is_admin=False):
    conn = get_db()
    cursor = conn.cursor()
    if is_admin:
        cursor.execute("DELETE FROM tests WHERE id = ?", (test_id,))
    else:
        cursor.execute("DELETE FROM tests WHERE id = ? AND user_id = ?", (test_id, user_id))
    rows = cursor.rowcount
    conn.commit()
    conn.close()
    return rows > 0

def get_dashboard_stats(user_id=None):
    """
    Computes overall statistics and retrieves the latest water quality test record.
    """
    conn = get_db()
    if user_id:
        filter_clause = "WHERE user_id = ?"
        params = (user_id,)
    else:
        filter_clause = ""
        params = ()

    total_tests = conn.execute(f"SELECT COUNT(*) FROM tests {filter_clause}", params).fetchone()[0]
    safe_tests = conn.execute(f"SELECT COUNT(*) FROM tests {filter_clause} {'AND' if user_id else 'WHERE'} status = 'Safe'", params).fetchone()[0]
    moderate_tests = conn.execute(f"SELECT COUNT(*) FROM tests {filter_clause} {'AND' if user_id else 'WHERE'} status = 'Moderate'", params).fetchone()[0]
    unsafe_tests = conn.execute(f"SELECT COUNT(*) FROM tests {filter_clause} {'AND' if user_id else 'WHERE'} status = 'Unsafe'", params).fetchone()[0]

    averages = conn.execute(f"""
        SELECT 
            COALESCE(ROUND(AVG(ph), 2), 0.0),
            COALESCE(ROUND(AVG(tds), 1), 0.0),
            COALESCE(ROUND(AVG(turbidity), 2), 0.0),
            COALESCE(ROUND(AVG(wqi_score), 1), 0.0)
        FROM tests {filter_clause}
    """, params).fetchone()

    # Retrieve latest test record
    latest_row = conn.execute(f"""
        SELECT * FROM tests {filter_clause}
        ORDER BY created_at DESC
        LIMIT 1
    """, params).fetchone()
    latest_test = dict(latest_row) if latest_row else None

    # Time series for charts
    chart_query = f"""
        SELECT id, sample_name, ph, tds, turbidity, wqi_score, status, strftime('%m/%d %H:%M', created_at) as test_time
        FROM tests {filter_clause}
        ORDER BY created_at ASC
        LIMIT 15
    """
    recent_trend = conn.execute(chart_query, params).fetchall()

    conn.close()

    return {
        "total_tests": total_tests,
        "safe_count": safe_tests,
        "moderate_count": moderate_tests,
        "unsafe_count": unsafe_tests,
        "safe_percentage": round((safe_tests / total_tests * 100), 1) if total_tests > 0 else 0,
        "avg_ph": averages[0],
        "avg_tds": averages[1],
        "avg_turbidity": averages[2],
        "avg_wqi": averages[3],
        "latest_test": latest_test,
        "trends": [dict(row) for row in recent_trend]
    }

def get_admin_stats():
    conn = get_db()
    total_users = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'user'").fetchone()[0]
    total_tests = conn.execute("SELECT COUNT(*) FROM tests").fetchone()[0]
    users_list = conn.execute("""
        SELECT u.id, u.username, u.custom_username, u.email, u.full_name, u.first_name, u.last_name, u.college_id, u.role, u.created_at,
               COUNT(t.id) as test_count
        FROM users u
        LEFT JOIN tests t ON u.id = t.user_id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """).fetchall()
    conn.close()
    return {
        "total_users": total_users,
        "total_tests": total_tests,
        "users": [dict(u) for u in users_list]
    }

def delete_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT role, email FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if row and (row["role"] == "admin" or row["email"] == "admin@waterguard.edu"):
        conn.close()
        return False, "Cannot delete system administrator account."
    
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True, "User deleted successfully."
