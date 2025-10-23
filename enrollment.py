"""
enrollment.py
Person 3 – Subject Enrolment System

Features:
- Enrol up to 4 subjects (auto ID, random mark 25–100)
- Remove subject
- Show all enrolled subjects with average & grade
- Change password
- Updates stored in Database (students.data)
"""

from __future__ import annotations
import random
from typing import Dict, Any, List
from validation import generate_subject_id
from database import Database

# ---------- Helper: mark to grade ----------
def mark_to_grade(mark: int) -> str:
    if mark >= 85: return "HD"
    if mark >= 75: return "D"
    if mark >= 65: return "C"
    if mark >= 50: return "P"
    return "Z"

# ---------- Subject class ----------
class Subject:
    """Represents a single enrolled subject with mark and grade."""
    def __init__(self, existing_ids: List[str] | None = None):
        self.id = generate_subject_id(existing_ids)
        self.mark = random.randint(25, 100)
        self.grade = mark_to_grade(self.mark)

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "mark": self.mark, "grade": self.grade}


# ---------- Student Enrolment System ----------
class StudentEnrolmentSystem:
    def __init__(self, db: Database, student: Dict[str, Any]):
        self.db = db
        self.student = student

    # ----------- Main Menu -----------
    def menu(self):
        while True:
            print("\n=== Subject Enrolment System ===")
            print("(e) Enrol subject")
            print("(r) Remove subject")
            print("(s) Show subjects")
            print("(p) Change password")
            print("(x) Exit")

            choice = (input("> ") or "").strip().lower()
            if choice == "e":
                self.enrol_subject()
            elif choice == "r":
                self.remove_subject()
            elif choice == "s":
                self.show_subjects()
            elif choice == "p":
                self.change_password()
            elif choice == "x":
                print("Exiting enrolment system...")
                break
            else:
                print("Invalid choice, please try again.")

    # ----------- Enrol Subject -----------
    def enrol_subject(self):
        subjects = self.student.get("subjects", [])
        if len(subjects) >= 4:
            print("You cannot enrol in more than 4 subjects.")
            return

        new_subject = Subject([s["id"] for s in subjects])
        subjects.append(new_subject.to_dict())
        self.student["subjects"] = subjects
        self._update_student_stats()
        self.db.update_student(self.student)

        print(f"Enrolled in subject {new_subject.id} | Mark: {new_subject.mark} | Grade: {new_subject.grade}")

    # ----------- Remove Subject -----------
    def remove_subject(self):
        subjects = self.student.get("subjects", [])
        if not subjects:
            print("You are not enrolled in any subjects.")
            return

        sid = input("Enter Subject ID to remove: ").strip()
        new_list = [s for s in subjects if s["id"] != sid]

        if len(new_list) == len(subjects):
            print("Subject ID not found.")
            return

        self.student["subjects"] = new_list
        self._update_student_stats()
        self.db.update_student(self.student)
        print(f"Subject {sid} removed successfully.")

    # ----------- Show Subjects -----------
    def show_subjects(self):
        subjects = self.student.get("subjects", [])
        if not subjects:
            print("No subjects enrolled.")
            return

        print("\n=== Your Enrolled Subjects ===")
        for s in subjects:
            print(f"  Subject ID: {s['id']} | Mark: {s['mark']} | Grade: {s['grade']}")

        avg = self.student.get("average", 0)
        grade = self.student.get("grade", "Z")
        status = self.student.get("status", "FAIL")
        print(f"\nAverage Mark: {avg:.2f}")
        print(f"Overall Grade: {grade} | Status: {status}")

    # ----------- Change Password -----------
    def change_password(self):
        old = input("Enter current password: ").strip()
        if old != self.student.get("password"):
            print("Incorrect password.")
            return

        new_pw = input("Enter new password: ").strip()
        if not new_pw:
            print("Password cannot be empty.")
            return

        self.student["password"] = new_pw
        self.db.update_student(self.student)
        print("Password updated successfully.")

    # ----------- Internal Helper -----------
    def _update_student_stats(self):
        subjects = self.student.get("subjects", [])
        if not subjects:
            self.student["average"] = 0.0
            self.student["grade"] = "Z"
            self.student["status"] = "FAIL"
            return

        avg = sum(s["mark"] for s in subjects) / len(subjects)
        self.student["average"] = round(avg, 2)
        self.student["grade"] = mark_to_grade(int(round(avg)))
        self.student["status"] = "PASS" if avg >= 50 else "FAIL"

