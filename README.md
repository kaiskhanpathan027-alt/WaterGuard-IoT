# Smart Water Quality Monitoring & Analysis System

**An Engineering College Capstone / Final Year Project**

### 🎓 Academic Project Details
- **Project Title:** Smart Water Quality Monitoring & Analysis System
- **Developed By:**
  1. **Kais Khan Fakirmat Khan** (Department of Computer Science and Design)
  2. **Rajeshwar Sandip Gaurkar** (Department of Computer Science and Design)
- **Institution:** Maharashtra Institute of Technology, Chhatrapati Sambhajinagar, Maharashtra
- **Department:** Computer Science and Design
- **Project Guide:** Vaishali Gaikwad Mam
- **Academic Year:** 2026–2027

Built using **HTML5, CSS3, JavaScript, Python Flask, SQLite, Chart.js, and ReportLab**.

---

## 🌟 Key Features

1. **Professional Home Page:**
   - Hero banner with animated telemetry, feature cards, and dynamic ripple graphics.
   - Comprehensive explanation of critical parameters (pH, TDS, Turbidity) mapped against **WHO & BIS IS 10500:2012** standards.
   - **Live Interactive Simulator:** Test sensory values in real-time right on the homepage without needing to log in.

2. **User Login and Registration:**
   - Secure session management with hashed passwords (`Werkzeug`).
   - Role-based authorization: **Student Analysts** and **System Administrators**.
   - Built-in **1-Click Demonstration Pre-fill buttons** on the login screen for seamless viva presentations.

3. **Dashboard with Real-Time Statistics:**
   - Key metric cards: Total Samples Tested, Safe count & percentage, Moderate count, Unsafe count.
   - Aggregated telemetry averages: Mean pH, Mean TDS, Mean Turbidity, and Mean System WQI.
   - Quick action shortcuts to record samples, download CSV datasets, and view audit history.

4. **Water Testing Terminal & Form:**
   - Form fields: Sample Designation, Sampling Location, Water Source category, pH, TDS, Turbidity, Analyst Name, and Remarks.
   - Synchronized numeric inputs and continuous range sliders.
   - **Real-Time Dynamic Gauge:** Calculates the Water Quality Index (WQI) and potability badge live as you slide or type!
   - 1-Click quick presets for Safe (Tap Water), Moderate (Borewell), and Unsafe (Contaminated Runoff).

5. **Automatic Water Quality Analysis:**
   - Weighted Arithmetic Water Quality Index (`WQI`) mathematical engine.
   - Weights: pH (0.35), TDS (0.35), Turbidity (0.30).
   - Instant calculation of sub-indices, individual parameter compliance, and overall safety rating.

6. **Results Classification (Safe, Moderate, Unsafe):**
   - **Safe (WQI 80–100):** Meets all WHO/BIS drinking standards; potable.
   - **Moderate (WQI 50–79):** Borderline mineral hardness or turbidity; basic filtration and boiling advised.
   - **Unsafe (WQI < 50 or severe breach):** Hazardous / contaminated; requires Reverse Osmosis (RO) and pathogen disinfection.
   - Detailed parameter diagnostic cards and tailored treatment recommendations.

7. **Interactive Graphs and Charts:**
   - **Multi-Parameter Trend Telemetry:** Interactive line chart with dual Y-axes tracking WQI, pH, Turbidity, and TDS across historical samples.
   - Toggle buttons to inspect specific parameter curves individually.
   - **Potability Distribution:** Doughnut chart illustrating Safe vs. Moderate vs. Unsafe sample proportions.

8. **Previous Test History:**
   - Searchable, filterable archive of past tests by status (All, Safe, Moderate, Unsafe) or location keyword.
   - One-click access to view detailed analytical certificates, download PDFs, or delete erroneous samples.
   - **CSV Dataset Export:** Export complete historical data for Excel or statistical analysis.

9. **Certified Downloadable PDF Reports:**
   - Official laboratory potability certificate generated dynamically in memory via **ReportLab**.
   - Features institutional header, unique certificate tracking ID, sample metadata, parameter compliance table against WHO standards, remediation protocol, and sign-off placeholders.

10. **Administrator Dashboard:**
    - High-level platform health metrics and system-wide statistics.
    - User account management table with roles, test counts, and removal capabilities.
    - Master inspection log of all tests conducted across all users.

---

## 🎨 Design & UI Architecture

- **Theme:** Modern Blue and White palette (Ocean Blue `#0284c7`, Deep Navy `#0f172a`, Electric Cyan `#06b6d4`, Crisp White `#ffffff`, and Cool Slate `#f8fafc`).
- **Glassmorphism:** Frosted translucent navigation bar (`backdrop-filter: blur(12px)`).
- **Responsive & Mobile-Friendly:** Fluid CSS Grid and Flexbox layouts with mobile hamburger navigation drawer.
- **Micro-Interactions & Animations:** Glowing pulse indicators on status badges, smooth card hover elevations, and dynamic radial gauges.

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.8 or higher installed on your computer.

### Step 1: Open Terminal in Project Folder
```bash
cd "c:\Users\Asfan\OneDrive\Desktop\water-quality-monitoring-system"
```

### Step 2: Install Required Dependencies
```bash
pip install -r requirements.txt
```
*(Packages installed: `Flask`, `reportlab`, `werkzeug`)*

### Step 3: Launch the Application
```bash
python app.py
```

### Step 4: Open in Web Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 Pre-Seeded Demo Accounts

The system automatically initializes an SQLite database (`water_quality.db`) and seeds ready-to-present sample data and accounts:

| Role | Username / Email | Password | Access Rights |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin@waterguard.edu` | `admin123` | Full control, User management, System-wide logs |
| **Demo Student Analyst** | `student@college.edu` | `student123` | Testing terminal, Personal history, PDF reports |

> **Viva Tip:** On the login page, you can simply click the **"Demo Student"** or **"Demo Admin"** button to auto-fill the login credentials instantly!

---

## 📁 Project Structure

```
water-quality-monitoring-system/
├── app.py                  # Core Flask controller, routes, APIs, auth
├── database.py             # SQLite database layer, schema, queries & seed data
├── water_quality.py        # Scientific WQI calculation engine & WHO rules
├── pdf_generator.py        # ReportLab laboratory certificate generator
├── requirements.txt        # Python dependency manifest
├── README.md               # Documentation & College Viva Guide
├── static/
│   ├── css/
│   │   └── style.css       # Modern responsive Blue & White stylesheet
│   └── js/
│       ├── main.js         # Client-side live preview & navigation logic
│       └── charts.js       # Chart.js trend lines & doughnut charts
└── templates/
    ├── base.html           # Master layout with glassmorphic navbar & footer
    ├── index.html          # Professional homepage & live simulator
    ├── about.html          # Engineering capstone specifications & sensor guide
    ├── login.html          # Sign-in page with 1-click demo autofill
    ├── register.html       # Student / Analyst registration
    ├── dashboard.html      # Telemetry analytics, cards, and charts
    ├── new_test.html       # Interactive testing form with live WQI gauge
    ├── test_result.html    # Detailed potability certificate & recommendations
    ├── history.html        # Historical test records with search and filters
    └── admin.html          # Administrator console & user management
```

---

## 🎓 College Viva & Presentation Tips

1. **Start on the Home Page:** Highlight the problem statement (waterborne diseases and non-continuous testing) and demonstrate the **Live Interactive Simulator** directly to the panel.
2. **Login as Demo Student:** Log in with one click to show session management.
3. **Showcase the Dashboard:** Point out the aggregated telemetry averages (mean pH, TDS, Turbidity) and dynamic Chart.js curves.
4. **Conduct a Live Test:** Go to "Test Sample", select "Moderate Preset" or adjust the sliders, showing how the live gauge reacts before submission.
5. **Demonstrate Automated Analysis:** Submit the test to reveal the **Potability Certificate** with parameter compliance table and treatment recommendations.
6. **Download PDF Report:** Click "Download Certified PDF Report" to present the formal, laboratory-grade certificate.
7. **Switch to Admin Account:** Show the **Administrator Console**, illustrating multi-user governance, system telemetry, and master dataset CSV export.
