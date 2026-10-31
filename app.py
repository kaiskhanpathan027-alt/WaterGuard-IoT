"""
Water Quality Monitoring System - Flask Application
College Engineering Project
"""

import os
import re
import csv
import io
from functools import wraps
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, g, jsonify, send_file, Response
)
from werkzeug.security import check_password_hash
import database as db
from water_quality import analyze_water_sample
from pdf_generator import generate_water_report_pdf

app = Flask(__name__)
app.config['SECRET_KEY'] = 'water-guard-sec-token-college-engg-2026'

# Ensure database is initialized on startup
with app.app_context():
    db.init_db()

# ----------------- Auth Decorators -----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('login', next=request.path))
        if session.get('role') != 'admin':
            flash("Administrator privileges required to access this resource.", "danger")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = db.get_user_by_id(user_id)

@app.context_processor
def inject_globals():
    return {
        'current_user': g.user,
        'current_year': '2026–2027',
        'system_title': "Smart Water Quality Monitoring & Analysis System",
        'college_name': "Maharashtra Institute of Technology, Chhatrapati Sambhajinagar, Maharashtra",
        'department_name': "Computer Science and Design",
        'guide_name': "Vaishali Gaikwad Mam",
        'developer_1': "Kais Khan Fakirmat Khan",
        'developer_2': "Rajeshwar Sandip Gaurkar",
        'academic_year': "2026–2027"
    }

# ----------------- Public Routes -----------------
@app.route('/')
def index():
    # If user is already logged in, they can explore or go directly to dashboard
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# ----------------- Authentication Routes -----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('dashboard'))

    prefill = request.args.get('prefill', '')

    if request.method == 'POST':
        login_input = request.form.get('login_input', '').strip()
        password = request.form.get('password', '').strip()

        if not login_input or not password:
            flash("Please enter your WaterGuard ID / email and password.", "danger")
            return render_template('login.html', login_input=login_input)

        # Allow login via custom username (firstname.lastname@water.guard), email, or legacy username
        user = db.get_user_by_login_identifier(login_input)

        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['custom_username'] = user['custom_username'] or user['username']
            session['role'] = user['role']
            session['full_name'] = user['full_name'] or user['username']
            
            flash(f"Welcome back, {session['full_name']}! ({session['custom_username']})", "success")
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials. Please verify your WaterGuard ID/email and password.", "danger")

    return render_template('login.html', login_input=prefill)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        college_id = request.form.get('college_id', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # Validation
        if not (first_name and last_name and email and password):
            flash("Please fill in First Name, Last Name, Email, and Password.", "danger")
            return render_template('register.html')

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "warning")
            return render_template('register.html')

        if password != confirm_password:
            flash("Passwords do not match. Please re-enter your password.", "warning")
            return render_template('register.html')

        user_id, custom_username, error = db.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            college_id=college_id,
            role="user"
        )
        if error:
            flash(error, "danger")
            return render_template('register.html')

        flash(f"Account registered successfully! Your unique WaterGuard ID is: {custom_username}. You can now sign in.", "success")
        return redirect(url_for('login', prefill=custom_username))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out safely.", "info")
    return redirect(url_for('login'))

# ----------------- User Dashboard & Testing -----------------
@app.route('/dashboard')
@login_required
def dashboard():
    stats = db.get_dashboard_stats(user_id=g.user['id'])
    recent_tests = db.get_user_tests(user_id=g.user['id'], limit=5)
    return render_template(
        'dashboard.html',
        stats=stats,
        latest_test=stats.get('latest_test'),
        recent_tests=recent_tests
    )

@app.route('/new-test', methods=['GET', 'POST'])
@login_required
def new_test():
    if request.method == 'POST':
        sample_name = request.form.get('sample_name', '').strip()
        location = request.form.get('location', '').strip()
        source_type = request.form.get('source_type', 'Tap Water').strip()
        ph_input = request.form.get('ph', '').strip()
        tds_input = request.form.get('tds', '').strip()
        turbidity_input = request.form.get('turbidity', '').strip()
        notes = request.form.get('notes', '').strip()
        tested_by = request.form.get('tested_by', '').strip() or g.user['full_name'] or g.user['username']

        # Validation
        try:
            ph = float(ph_input)
            tds = float(tds_input)
            turbidity = float(turbidity_input)
        except ValueError:
            flash("Please enter valid numeric values for pH, TDS, and Turbidity.", "danger")
            return render_template('new_test.html')

        if not (0.0 <= ph <= 14.0):
            flash("pH value must be between 0.0 and 14.0.", "warning")
            return render_template('new_test.html')

        if tds < 0 or tds > 10000:
            flash("TDS must be a positive value within 0 - 10,000 mg/L.", "warning")
            return render_template('new_test.html')

        if turbidity < 0 or turbidity > 1000:
            flash("Turbidity must be a positive value within 0 - 1000 NTU.", "warning")
            return render_template('new_test.html')

        if not sample_name or not location:
            flash("Sample Name and Sampling Location are required.", "warning")
            return render_template('new_test.html')

        test_id, analysis = db.save_test(
            user_id=g.user['id'],
            sample_name=sample_name,
            location=location,
            source_type=source_type,
            ph=ph,
            tds=tds,
            turbidity=turbidity,
            notes=notes,
            tested_by=tested_by
        )

        flash(f"Water sample analyzed successfully! Result: {analysis['overall_status']}.", "success")
        return redirect(url_for('test_result', test_id=test_id))

    return render_template('new_test.html')

@app.route('/test/<int:test_id>')
@login_required
def test_result(test_id):
    test = db.get_test_by_id(test_id)
    if not test:
        flash("Test record not found.", "danger")
        return redirect(url_for('dashboard'))

    # Security: users can view only their tests unless admin
    if test['user_id'] != g.user['id'] and g.user['role'] != 'admin':
        flash("Access denied. You do not have permission to view this test.", "danger")
        return redirect(url_for('dashboard'))

    analysis = analyze_water_sample(test['ph'], test['tds'], test['turbidity'])
    return render_template('test_result.html', test=test, analysis=analysis)

@app.route('/history')
@login_required
def history():
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'all').strip()
    date_filter = request.args.get('date', '').strip()

    tests = db.get_user_tests(
        user_id=g.user['id'],
        search=search,
        status_filter=status_filter,
        date_filter=date_filter
    )
    all_tests = db.get_user_tests(user_id=g.user['id'])
    return render_template(
        'history.html',
        tests=tests,
        search=search,
        status_filter=status_filter,
        date_filter=date_filter,
        total_count=len(tests),
        all_count=len(all_tests)
    )

@app.route('/delete-test/<int:test_id>', methods=['POST'])
@login_required
def delete_test(test_id):
    test = db.get_test_by_id(test_id)
    if not test:
        flash("Record not found.", "warning")
        return redirect(url_for('history'))

    is_admin = (g.user['role'] == 'admin')
    if test['user_id'] != g.user['id'] and not is_admin:
        flash("Access Denied: You cannot delete another user's test records.", "danger")
        return redirect(url_for('history'))

    success = db.delete_test(test_id, user_id=g.user['id'], is_admin=is_admin)
    if success:
        flash(f"Water test sample #{test_id} was deleted successfully.", "success")
    else:
        flash("Could not delete record. You may not have authorization.", "danger")
    
    referrer = request.referrer
    if referrer and ('admin' in referrer or 'history' in referrer or 'dashboard' in referrer):
        return redirect(referrer)
    return redirect(url_for('history'))

@app.route('/report/pdf/<int:test_id>')
@login_required
def download_pdf(test_id):
    test = db.get_test_by_id(test_id)
    if not test:
        flash("Test record not found.", "danger")
        return redirect(url_for('dashboard'))

    # Security check: User can only download their own tests unless admin
    if test['user_id'] != g.user['id'] and g.user['role'] != 'admin':
        flash("Access Denied: You can only download reports for your own tests.", "danger")
        return redirect(url_for('dashboard'))

    pdf_buffer = generate_water_report_pdf(dict(test))
    clean_sample_name = re.sub(r'[^a-zA-Z0-9_]', '_', test['sample_name'][:20])
    filename = f"WaterGuard_Report_Sample_{test['id']}_{clean_sample_name}.pdf"
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

@app.route('/export-csv')
@login_required
def export_csv():
    is_admin = (g.user['role'] == 'admin')
    if is_admin and request.args.get('scope') == 'all':
        tests = db.get_all_tests()
    else:
        tests = db.get_user_tests(user_id=g.user['id'])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Test ID", "Sample Name", "Location", "Source Type",
        "pH Level", "TDS (mg/L)", "Turbidity (NTU)", "WQI Score",
        "Overall Status", "Tested By", "Date Tested", "Remarks"
    ])

    for t in tests:
        writer.writerow([
            t['id'], t['sample_name'], t['location'], t['source_type'],
            t['ph'], t['tds'], t['turbidity'], t['wqi_score'],
            t['status'], t['tested_by'], t['created_at'], t['notes'] or ''
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=Water_Quality_Dataset_{datetime.now().strftime('%Y%m%d')}.csv"}
    )

# ----------------- Admin Routes -----------------
@app.route('/admin')
@admin_required
def admin_dashboard():
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'all').strip()

    admin_data = db.get_admin_stats()
    sys_stats = db.get_dashboard_stats(user_id=None) # all tests
    all_tests = db.get_all_tests(search=search, status_filter=status_filter)

    return render_template(
        'admin.html',
        admin_data=admin_data,
        sys_stats=sys_stats,
        all_tests=all_tests,
        search=search,
        status_filter=status_filter
    )

@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    success, msg = db.delete_user(user_id)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")
    return redirect(url_for('admin_dashboard'))

# ----------------- AJAX / JSON APIs -----------------
@app.route('/api/analyze-preview', methods=['POST'])
def api_analyze_preview():
    data = request.get_json(silent=True) or request.form
    try:
        ph = float(data.get('ph', 7.0))
        tds = float(data.get('tds', 200.0))
        turbidity = float(data.get('turbidity', 1.0))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid numerical parameters"}), 400

    analysis = analyze_water_sample(ph, tds, turbidity)
    return jsonify(analysis)

@app.route('/api/dashboard-charts')
@login_required
def api_dashboard_charts():
    scope = request.args.get('scope', 'user')
    user_id = None if (scope == 'all' and g.user['role'] == 'admin') else g.user['id']
    stats = db.get_dashboard_stats(user_id=user_id)

    # Format chart data
    trend_labels = [row['test_time'] for row in stats['trends']]
    ph_data = [row['ph'] for row in stats['trends']]
    tds_data = [row['tds'] for row in stats['trends']]
    turb_data = [row['turbidity'] for row in stats['trends']]
    wqi_data = [row['wqi_score'] for row in stats['trends']]
    sample_names = [row['sample_name'] for row in stats['trends']]

    chart_payload = {
        "status_distribution": {
            "labels": ["Safe", "Moderate", "Unsafe"],
            "data": [stats['safe_count'], stats['moderate_count'], stats['unsafe_count']],
            "colors": ["#10b981", "#f59e0b", "#ef4444"]
        },
        "trends": {
            "labels": trend_labels,
            "sample_names": sample_names,
            "ph": ph_data,
            "tds": tds_data,
            "turbidity": turb_data,
            "wqi": wqi_data
        },
        "summary": {
            "avg_ph": stats['avg_ph'],
            "avg_tds": stats['avg_tds'],
            "avg_turbidity": stats['avg_turbidity'],
            "avg_wqi": stats['avg_wqi']
        }
    }
    return jsonify(chart_payload)

if __name__ == '__main__':
    print("==================================================")
    print("Water Quality Monitoring System - Flask App")
    print("Running on http://127.0.0.1:5000")
    print("Demo Admin:   admin@waterguard.edu   / admin123")
    print("Demo Student: student@college.edu    / student123")
    print("==================================================")
    app.run(debug=True, host='127.0.0.1', port=5000)
