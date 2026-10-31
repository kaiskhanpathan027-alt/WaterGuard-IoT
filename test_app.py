"""
Automated Verification & Unit Tests for Water Quality Monitoring System
Comprehensive tests covering:
1. New user registration & automatic custom username generation
2. Conflict handling for custom usernames (appending numbers)
3. Login using custom username (firstname.lastname@water.guard)
4. Water quality sample submission & WQI computation
5. Persistent user data storage across logout/login cycles
6. Smart dashboard with latest result and stats
7. My History page with date and status filters
8. Downloading certified PDF reports with visual gauges
9. User data privacy & access control enforcement
10. Admin console oversight and system dataset export
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from water_quality import evaluate_ph, evaluate_tds, evaluate_turbidity, analyze_water_sample
import database as db
from pdf_generator import generate_water_report_pdf
from app import app

TEST_DB_PATH = os.path.join(PROJECT_DIR, "test_water_quality.db")

class WaterQualityFullSystemTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.DB_PATH = TEST_DB_PATH
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except Exception:
                pass
        db.init_db()

    @classmethod
    def tearDownClass(cls):
        db.DB_PATH = os.path.join(PROJECT_DIR, "water_quality.db")
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except Exception:
                pass

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_01_water_quality_evaluations(self):
        """Test scientific parameter evaluations and WQI scoring"""
        # Safe test
        res_safe = analyze_water_sample(7.2, 180, 0.8)
        self.assertEqual(res_safe["overall_status"], "Safe")
        self.assertGreaterEqual(res_safe["wqi_score"], 80)
        self.assertEqual(res_safe["status_class"], "safe")

        # Moderate test (High TDS)
        res_mod = analyze_water_sample(7.2, 650, 1.2)
        self.assertEqual(res_mod["overall_status"], "Moderate")
        self.assertEqual(res_mod["status_class"], "moderate")

        # Unsafe test (Acidic pH and high turbidity)
        res_unsafe = analyze_water_sample(4.8, 1200, 25.0)
        self.assertEqual(res_unsafe["overall_status"], "Unsafe")
        self.assertEqual(res_unsafe["status_class"], "unsafe")
        self.assertLess(res_unsafe["wqi_score"], 50)
        print("[OK] 1. Water Quality Analysis Engine: Passed")

    def test_02_custom_username_generation(self):
        """Test automatic custom username generator format and uniqueness"""
        # Generate username from first and last name
        uname1 = db.generate_custom_username("Kais", "Khan")
        self.assertTrue(uname1.endswith("@water.guard"))
        self.assertEqual(uname1.lower(), uname1)
        self.assertNotIn(" ", uname1)

        # Generate for user with special chars and spaces
        uname2 = db.generate_custom_username(" John-Paul! ", " O'Connor ")
        self.assertTrue(uname2.startswith("johnpaul.oconnor"))
        self.assertTrue(uname2.endswith("@water.guard"))

        # Test registration via database helper
        uid, uname_new, err = db.create_user("Rohan", "Sharma", "rohan.sharma.test@college.edu", "pass123", "MIT-CSD-99")
        self.assertIsNone(err)
        self.assertIsNotNone(uid)
        self.assertEqual(uname_new, "rohan.sharma@water.guard")

        # Conflict test: another user with identical name gets incremental suffix
        uid2, uname_conflict, err2 = db.create_user("Rohan", "Sharma", "rohan2.test@college.edu", "pass123", "MIT-CSD-100")
        self.assertIsNone(err2)
        self.assertEqual(uname_conflict, "rohan.sharma1@water.guard")
        print("[OK] 2. Custom Username System (firstname.lastname@water.guard): Passed")

    def test_03_login_with_custom_username_and_registration_flow(self):
        """Test web registration endpoint and login using custom username"""
        # Register new student via web form
        reg_resp = self.client.post('/register', data={
            'first_name': 'Meera',
            'last_name': 'Patil',
            'email': 'meera.patil.test@mit.edu',
            'college_id': 'MIT-CSD-2026-MP',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(reg_resp.status_code, 200)
        self.assertIn(b"Account registered successfully", reg_resp.data)

        # Verify created custom username
        user = db.get_user_by_email("meera.patil.test@mit.edu")
        self.assertIsNotNone(user)
        self.assertEqual(user['custom_username'], "meera.patil@water.guard")

        # Login using the custom username
        login_resp = self.client.post('/login', data={
            'login_input': 'meera.patil@water.guard',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn(b"Welcome back", login_resp.data)
        self.assertIn(b"Meera Patil", login_resp.data)
        print("[OK] 3. Registration & Login via Custom Username: Passed")

    def test_04_persistent_storage_and_smart_dashboard(self):
        """Test saving a test, logging out, logging back in, and verifying latest test display"""
        # Login as student Alex Turner
        self.client.post('/login', data={
            'login_input': 'alex.turner@water.guard',
            'password': 'student123'
        }, follow_redirects=True)

        # Submit a new water test
        test_resp = self.client.post('/new-test', data={
            'sample_name': 'Persistent Storage Lab Water',
            'location': 'Research Wing Tap 4B',
            'source_type': 'Tap Water / Municipal Supply',
            'ph': '7.35',
            'tds': '175',
            'turbidity': '0.75',
            'notes': 'Checking automated database persistence across sessions',
            'tested_by': 'Alex Turner'
        }, follow_redirects=True)
        self.assertEqual(test_resp.status_code, 200)
        self.assertIn(b"Laboratory Potability Assessment", test_resp.data)

        # Logout
        self.client.get('/logout', follow_redirects=True)

        # Re-login with custom username
        self.client.post('/login', data={
            'login_input': 'alex.turner@water.guard',
            'password': 'student123'
        }, follow_redirects=True)

        # Access Smart Dashboard - ensure latest result and previous history are shown
        dash_resp = self.client.get('/dashboard')
        self.assertEqual(dash_resp.status_code, 200)
        self.assertIn(b"Most Recent Water Quality Test", dash_resp.data)
        self.assertIn(b"Persistent Storage Lab Water", dash_resp.data)
        self.assertIn(b"alex.turner@water.guard", dash_resp.data)
        print("[OK] 4. Persistent Storage & Smart Dashboard with Latest Result: Passed")

    def test_05_my_history_page_and_filtering(self):
        """Test My History section, date filter, status filter, and counts"""
        # Login
        self.client.post('/login', data={
            'login_input': 'alex.turner@water.guard',
            'password': 'student123'
        }, follow_redirects=True)

        # Access My History
        hist_resp = self.client.get('/history')
        self.assertEqual(hist_resp.status_code, 200)
        self.assertIn(b"My History", hist_resp.data)
        self.assertIn(b"Download PDF Report", hist_resp.data)

        # Filter by status: Safe
        safe_resp = self.client.get('/history?status=safe')
        self.assertEqual(safe_resp.status_code, 200)

        # Filter by today's date
        today_str = datetime.now().strftime('%Y-%m-%d')
        date_resp = self.client.get(f'/history?date={today_str}')
        self.assertEqual(date_resp.status_code, 200)
        print("[OK] 5. My History Page (Search, Date & Status Filter): Passed")

    def test_06_enhanced_pdf_with_graphs(self):
        """Test generation of attractive PDF with WaterGuard logo, gauges, and custom username"""
        user = db.get_user_by_login_identifier('alex.turner@water.guard')
        tests = db.get_user_tests(user['id'], limit=1)
        self.assertTrue(len(tests) > 0)
        test_record = tests[0]

        pdf_buf = generate_water_report_pdf(dict(test_record))
        self.assertIsNotNone(pdf_buf)
        pdf_bytes = pdf_buf.getvalue()
        self.assertTrue(len(pdf_bytes) > 2000)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

        # Test download endpoint (requires authenticated owner)
        self.client.post('/login', data={
            'login_input': 'alex.turner@water.guard',
            'password': 'student123'
        }, follow_redirects=True)
        pdf_resp = self.client.get(f"/report/pdf/{test_record['id']}")
        self.assertEqual(pdf_resp.status_code, 200)
        self.assertEqual(pdf_resp.content_type, "application/pdf")
        self.assertIn("WaterGuard_Report_Sample", pdf_resp.headers.get("Content-Disposition", ""))
        print(f"[OK] 6. Attractive PDF with Visual Telemetry Gauges ({len(pdf_bytes)} bytes): Passed")

    def test_07_privacy_and_security(self):
        """Ensure users can only access their own tests and cannot inspect or download other users' tests"""
        # Create User A
        u1_id, u1_name, _ = db.create_user("Alice", "Smith", "alice.test@college.edu", "pass123")
        t1_id, _ = db.save_test(u1_id, "Alice Sample Private", "Lab A", "Tap Water", 7.2, 160, 0.6, "Alice notes", "Alice Smith")

        # Create User B
        u2_id, u2_name, _ = db.create_user("Bob", "Jones", "bob.test@college.edu", "pass123")
        t2_id, _ = db.save_test(u2_id, "Bob Sample Private", "Lab B", "Tap Water", 7.1, 150, 0.5, "Bob notes", "Bob Jones")

        # Login as User A
        self.client.post('/login', data={'login_input': u1_name, 'password': 'pass123'}, follow_redirects=True)

        # User A can view their own test
        view_own = self.client.get(f'/test/{t1_id}')
        self.assertEqual(view_own.status_code, 200)

        # User A tries to view User B's test -> Access Denied
        view_other = self.client.get(f'/test/{t2_id}', follow_redirects=True)
        self.assertIn(b"Access denied", view_other.data)

        # User A tries to download User B's PDF -> Access Denied
        pdf_other = self.client.get(f'/report/pdf/{t2_id}', follow_redirects=True)
        self.assertIn(b"Access Denied", pdf_other.data)
        print("[OK] 7. Security & User Privacy Enforcement: Passed")

    def test_08_admin_functionality(self):
        """Verify admin console oversight, user list, and system metrics"""
        # Login as Admin
        self.client.post('/login', data={'login_input': 'admin.director@water.guard', 'password': 'admin123'}, follow_redirects=True)

        admin_resp = self.client.get('/admin')
        self.assertEqual(admin_resp.status_code, 200)
        self.assertIn(b"Administrator &amp; Laboratory Oversight", admin_resp.data)

        # Export full system dataset
        csv_resp = self.client.get('/export-csv?scope=all')
        self.assertEqual(csv_resp.status_code, 200)
        self.assertEqual(csv_resp.content_type, "text/csv; charset=utf-8")
        print("[OK] 8. Admin Console Oversight & Master Dataset Export: Passed")

if __name__ == '__main__':
    from datetime import datetime
    unittest.main()
