# dormitory_management_system
CSC3170_individual_project

This project is a **web-based Dormitory Management System** for managing student housing. It supports three user roles: **Students**, **Tutors**, and **Wardens**, with secure authentication, detailed validation, and dynamic UI feedback.

---

## 🧱 Features Overview

### 👩‍🎓 Student

1. **Login and Authentication**  
   - Log in using **student ID** (9-digit number) and **hashed password**.  
   - Invalid credentials show:  
     - `"User ID or password incorrect"` if password does not match.  
     - `"Please enter a valid ID or password"` if ID is less than 9 digits.  
   - Blank inputs trigger: `"Please fill in this field"`.  

2. **View and Update Personal Information**  
   - Display: name, gender, student ID, email, school, major, phone number.  
   - Phone number editing:
     - Only 11-digit numbers starting with `1` are valid.  
     - Blank input → `"Please fill in this field"`.  
     - Non-numeric input → `"Phone number format is incorrect"`.  
     - Input identical to current → `"Phone number has not changed"`.  

3. **View Dormitory Information**
   - Shows building, floor, room, bed, electricity balance, pending and processed application counts.  
   - **Electricity Recharge:**
     - Minimum recharge: 10 CNY, integer only.  
     - Blank input → `"Please fill in this field"`.  
     - Non-numeric input → `"Invalid input"`.  
     - Decimal input → system rounds to nearest valid integer.  
     - Value < 10 → `"Value must be greater than 10"`.  
   - **Electricity balance display:**
     - If balance < 0 → displayed in **red**.  
     - If balance > 0 → displayed in **green**.  

4. **Submit Dormitory Adjustment Application**
   - Selection sequence must be **Building → Floor → Room → Bed**.  
   - Floor-gender constraints:
     - Males can only choose floors 2, 4, 6, 8.  
     - Females can only choose floors 3, 5, 7.  
   - Rooms and beds selection:
     - Only rooms with available beds are selectable.  
     - Only beds that are empty are selectable.  
   - Submission validation:
     - If any step incomplete → prompt `"Please complete all selections"`.  
     - Submissions are sent to the corresponding building **warden**.

5. **Submit Maintenance Request**
   - Choose maintenance type and submit.  
   - Validation:
     - If fields incomplete → `"Please complete all selections"`.  
   - Submission sent to the **floor tutor**.  

---

### 👨‍🏫 Tutor
1. **Login and Personal Info** (Same as student). 
   - Display name, gender, tutor ID, email, phone number.  
   - Editable field: phone number (validated format).  
2. **Edit Phone Number** – same rules as above.  
3. **Process Maintenance Requests**
   - Options: Approve or Reject.  
   - After processing:
     - `"Maintenance request approved"`  
     - `"Maintenance request rejected"`  
   - Pending and processed counts update dynamically.  

4. **View Students and Dormitory Status**
   - Shows all students on the floors managed.  
   - Sorted by room number + bed number.  

---

### 🧍‍♂️ Warden

1. **Login and Personal Info** – same validation as students.  
2. **View Tutors**
   - Shows tutor info including pending application counts.  
   - Sorted by floor managed.  

3. **View Students**
   - Sorted by room number + bed number.  

4. **Monitor Dormitory Occupancy**
   - Displays total beds, occupied beds, available beds, and electricity balance.  
   - Available beds = 0 → displayed in **red**; otherwise **green**.  

5. **Process Dormitory Adjustment Requests**
   - Approve or reject student dormitory transfer applications.  
   - Upon approval:
     - Student's dormitory info updated.  
     - Room counts updated automatically.  
   - Upon rejection:
     - Room occupancy updated but student info remains unchanged.  
   - Prompt messages:
     - `"Dormitory adjustment request approved"`  
     - `"Dormitory adjustment request rejected"`  

---

## 🎨 Aesthetic Design

- **Background:** Dormitory exterior image.  
- **Container:** Glass-blur (frosted-glass) style.  
- **Animations:** Fade-in for all pages.  
- **Table Rows:** Highlighted in gray when selected.  
- **Tabs:** Gradient buttons, glow when active.  
- **Buttons:** Hover floating and color deepening effects.  

---

## 🎨 Aesthetic Design

- Background: dormitory exterior image.  
- Main container: glass blur (“frosted glass”) style.  
- Smooth **fade-in animation** for every page.  
- Table rows **highlighted in gray** when selected.  
- Tab buttons: gradient colors, glowing when selected.  
- Buttons: hover floating and color deepening effects for interactivity.

---

## 🧩 System Architecture

**Frontend:**  
- `index.html`, `style.css`, `script.js`  
- Implemented using HTML, CSS, and JavaScript.  
- Communicates with backend through `fetch()` (JSON-based REST API).  

**Backend:**  
- Framework: **Flask (Python)**  
- Database: **MySQL**  
- Libraries:
  ```python
  from flask import Flask, request, jsonify
  from flask_mysqldb import MySQL
  from flask_cors import CORS
  from werkzeug.security import check_password_hash
  import pandas, pymysql, logging, os

Data Flow Example:
- Frontend sends login info to /login (POST).
- Backend validates credentials (hashed password check).
- Returns JSON result with status and user data.
- Frontend updates UI dynamically based on response.

🔒 Security
All passwords are hashed before being stored in the database.
The PASSWORD column remains for testing and grading only, containing plain text for reference.
Backend validation prevents SQL injection and handles all user input errors gracefully.

🧰 Installation & Setup
Step 1. Install Dependencies
  pip install flask flask-mysqldb flask-cors pymysql pandas werkzeug

Step 2. Initialize Database
Run the following scripts in order:
- mysql_class.py – defines helper SQL methods.
- table_generated.py – drops existing tables and recreates new ones.
- insert_data.py – inserts initial data.
- secure_init_password.py – hashes all plaintext passwords.

Step 3. Run Backend
python app.py
Keep this running.

Step 4. Run Frontend
Open index.html with Live Server in VS Code.
> Tip: Some HTML5 validation messages (e.g., "Please fill in this field") are displayed in the browser's language. For consistent English messages, set your browser language to English before testing.

💡 Notes
Every dropdown menu and input validation is dynamically linked to backend data.
Error messages are shown inline with visual highlights.
Each role interacts only with data within their permission scope.