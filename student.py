"""
student.py
Student System (Person 2) — login/register/exit

Uses shared modules:
- database.py  → Database (find_by_email, load_students, add_student)
- validation.py → is_valid_email, is_valid_password, generate_student_id, validate_menu_choice, notify

Provides:
- Student model (class Student)
- StudentSystem class with menu()
"""

from __future__ import annotations
from typing import Optional, Dict, Any
from database import Database
from validation import (
    is_valid_email,
    is_valid_password,
    generate_student_id,
    validate_menu_choice,
    notify,
)

StudentDict = Dict[str, Any]

class Student:
    def __init__(self, sid: str, name: str, email: str, password: str):
        self.id = sid
        self.name = name
        self.email = email
        self.password = password
        self.subjects: list[dict] = []
        self.average: float = 0.0
        self.grade: str = "Z"
        self.status: str = "FAIL"

    def to_dict(self) -> StudentDict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "subjects": self.subjects,
            "average": self.average,
            "grade": self.grade,
            "status": self.status,
        }

class StudentSystem:
    def __init__(self, db: Database):
        self.db = db

    def menu(self) -> Optional[StudentDict]:
        """Top-level Student menu. Returns the logged-in student dict, or None on exit."""
        allowed = {"l", "r", "x"}

        while True:
            print("\n--- Student Menu ---")
            print("(l) login")
            print("(r) register")
            print("(x) exit")
            choice = (input("Enter choice: ") or "").strip().lower()

            if not validate_menu_choice(choice, allowed):
                notify("Invalid choice. Use l, r, or x.")
                continue

            if choice == "l":
                stu = self.login_student()
                if stu:
                    notify(f"Welcome back, {stu.get('name', 'student')}!")
                    return stu   # enrolment launched by UniversityApp
            elif choice == "r":
                self.register_student()
            else:  # "x"
                notify("Returning to main menu.")
                return None

    def register_student(self) -> None:
        print("\n--- Register --- (press x to cancel)")
        name = input("Name: ").strip()
        if name.lower() == "x": return
        email = input("Email: ").strip()
        if email.lower() == "x": return
        password = input("Password: ").strip()
        if password.lower() == "x": return

        if not name:
            notify("Name cannot be empty.")
            return
        if not is_valid_email(email):
            notify("Invalid email. Must end with @university.com")
            return
        if not is_valid_password(password):
            notify("Invalid password. Start with uppercase, 5+ letters, then 3+ digits.")
            return

        if self.db.find_by_email(email):
            notify("A student with that email already exists.")
            return

        students = self.db.load_students()
        new_id = generate_student_id([str(s.get("id")) for s in students])
        student = Student(new_id, name, email, password)
        if self.db.add_student(student.to_dict()):
            notify(f"Registration successful! Your ID is {new_id}")
        else:
            notify("Registration failed (duplicate or write error).")

    def login_student(self) -> Optional[StudentDict]:
        print("\n--- Login --- (press x to cancel)")
        email = input("Email: ").strip()
        if email.lower() == "x": return None
        password = input("Password: ").strip()
        if password.lower() == "x": return None

        if not is_valid_email(email) or not is_valid_password(password):
            notify("Invalid credentials format.")
            return None

        s = self.db.find_by_email(email)
        if s and s.get("password") == password:
            return s

        notify("Invalid credentials.")
        return None

if __name__ == "__main__":
    db = Database("students.data")
    StudentSystem(db).menu()
