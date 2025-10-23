"""
university.py
University System + Authentication routing

Person 1 – University System + Authentication
---------------------------------------------
- Main menu: (a) admin / (s) student / (x) exit
- Admin → AdminSystem (requires admin login)
- Student → StudentSystem (Person 2) or fallback register/login
- After successful student login → Subject Enrolment System (Person 3)
"""

from __future__ import annotations
from typing import Any, Dict, Optional

from database import Database
from admin import AdminSystem
from validation import is_valid_email, is_valid_password, generate_student_id

# -------- Admin auth config --------
REQUIRE_ADMIN_LOGIN = True
ADMIN_EMAIL = "admin@university.com"
ADMIN_PASSWORD = "Admin2000"   # Meets rule: Uppercase + ≥5 letters + ≥3 digits

# Try importing Person 2 (Student System)
try:
    from student import StudentSystem  # must return a logged-in student dict on success
except ImportError:
    StudentSystem = None  # type: ignore

# Try importing Person 3 (Enrolment System)
try:
    from enrollment import StudentEnrolmentSystem
except ImportError:
    StudentEnrolmentSystem = None  # type: ignore


# ---------- small utility ----------
def _is_exit(token: str) -> bool:
    token = (token or "").strip().lower()
    return token in {"x", "q", "quit", "exit"}


class UniversityApp:
    def __init__(self, db: Database):
        self.db = db
        self.admin_sys = AdminSystem(db)
        self.student_sys = StudentSystem(db) if StudentSystem else None

    # ----------------- University Menu -----------------
    def start(self) -> None:
        while True:
            print("\n=== University System ===")
            print("(a) admin")
            print("(s) student")
            print("(x) exit")
            choice = (input("> ") or "").strip().lower()

            if choice == "a":
                if not REQUIRE_ADMIN_LOGIN or self._admin_login():
                    self.admin_sys.menu()
                else:
                    print("Admin login failed.")

            elif choice == "s":
                self._student_entrypoint()

            elif _is_exit(choice):
                print("Goodbye!")
                break

            else:
                print("Invalid option. Please try again.")

    # ----------------- Admin login (required if enabled) -----------------
    def _admin_login(self) -> bool:
        """
        Fixed-credential admin login with validation and up to 3 attempts.
        Uses the same email/password rules as students for consistency.
        """
        print("\n--- Admin Login ---")
        attempts = 3
        while attempts > 0:
            email = input("Email: ").strip()
            password = input("Password: ").strip()

            # Optional: reuse validation rules for consistency
            if not is_valid_email(email):
                print("Invalid email format. Must end with @university.com.")
                attempts -= 1
                continue
            if not is_valid_password(password):
                print("Invalid password format (Uppercase + 5+ letters + 3+ digits).")
                attempts -= 1
                continue

            if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                print("Login successful. Welcome, Admin!")
                return True

            print("Incorrect admin credentials.")
            attempts -= 1

        return False

    # ----------------- Student entrypoint -----------------
    def _student_entrypoint(self) -> None:
        if self.student_sys is not None:
            # Use Person 2's system
            student = self.student_sys.menu()
            self._launch_enrolment_if_ready(student)
        else:
            # Fallback mini student system
            self._student_menu_fallback()

    # ----------------- Fallback Student Menu -----------------
    def _student_menu_fallback(self) -> None:
        while True:
            print("\n--- Student System (Fallback) ---")
            print("(l) login")
            print("(r) register")
            print("(x) exit")
            choice = (input("> ") or "").strip().lower()

            if choice == "l":
                student = self._login_flow_fallback()
                self._launch_enrolment_if_ready(student)
            elif choice == "r":
                self._register_flow_fallback()
            elif _is_exit(choice):
                return
            else:
                print("Invalid option. Please try again.")

    # ----------------- Enrolment launcher -----------------
    def _launch_enrolment_if_ready(self, student: Optional[Dict[str, Any]]) -> None:
        if student:
            if StudentEnrolmentSystem is not None:
                StudentEnrolmentSystem(self.db, student).menu()
            else:
                print("Enrolment system not found (missing enrollment.py).")

    # ----------------- Login (Fallback) -----------------
    def _login_flow_fallback(self) -> Optional[Dict[str, Any]]:
        email = input("Enter email (or 'x' to cancel): ").strip()
        if _is_exit(email):
            print("Login cancelled.")
            return None

        password = input("Enter password (or 'x' to cancel): ").strip()
        if _is_exit(password):
            print("Login cancelled.")
            return None

        if not is_valid_email(email):
            print("Error: invalid email format. Must end with @university.com.")
            return None
        if not is_valid_password(password):
            print("Error: invalid password format (uppercase + 5 letters + 3 digits).")
            return None

        student = self.db.find_by_email(email)
        if student and student.get("password") == password:
            print(f"Login successful. Welcome, {student.get('name', 'student')}!")
            return student

        print("Login failed. Please check your credentials.")
        return None

    # ----------------- Register (Fallback) -----------------
    def _register_flow_fallback(self) -> None:
        name = input("Enter name (or 'x' to cancel): ").strip()
        if _is_exit(name):
            print("Registration cancelled.")
            return

        email = input("Enter email (or 'x' to cancel): ").strip()
        if _is_exit(email):
            print("Registration cancelled.")
            return

        password = input("Enter password (or 'x' to cancel): ").strip()
        if _is_exit(password):
            print("Registration cancelled.")
            return

        if not name:
            print("Error: name cannot be empty.")
            return
        if not is_valid_email(email):
            print("Error: invalid email format. Must end with @university.com.")
            return
        if not is_valid_password(password):
            print("Error: invalid password format (uppercase + 5 letters + 3 digits).")
            return
        if self.db.find_by_email(email):
            print("Registration failed. Student already exists.")
            return

        existing_ids = [str(s.get("id")) for s in self.db.get_all()]
        sid = generate_student_id(existing_ids)
        student = {
            "id": sid,
            "name": name,
            "email": email,
            "password": password,
            "subjects": [],
            "average": 0.0,
            "grade": "Z",
            "status": "FAIL",
        }

        if self.db.add_student(student):
            print(f"Registration successful. Your Student ID is {sid}.")
            print("You can now log in and manage enrolments.")
        else:
            print("Registration failed (duplicate or write error).")


# ----------------- Run Standalone -----------------
if __name__ == "__main__":
    app = UniversityApp(Database("students.data"))
    app.start()
