
# enrollment.py
"""
Person 3 – Subject Enrolment System

Features:
- Enrol up to four (4) subjects (auto ID, random mark 25–100)
- Remove subject by ID
- Show all enrolled subjects with average & overall grade
- Change password (uses shared validation rule)
- All updates persisted via Database (students.data)
"""

from _future_ import annotations
import random
from typing import Dict, Any, List

from validation import (
    generate_subject_id,
    is_valid_password,
    validate_menu_choice,
)
from database import Database


# ---------- Helper: mark -> grade ----------
def mark_to_grade(mark: int) -> str:
    if mark >= 85:
        return "HD"
    if mark >= 75:
        return "D"
    if mark >= 65:
        return "C"
    if mark >= 50:
        return "P"
    return "Z"


# ---------- Subject ----------
class Subject:
    """Represents a single enrolled subject with mark and grade."""
    def _init_(self, existing_ids: List[str] | None = None):
        self.id = generate_subject_id(existing_ids)
        self.mark = random.randint(25, 100)
        self.grade = mark_to_grade(self.mark)

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "mark": self.mark, "grade": self.grade}


# ---------- Student Enrolment System ----------
class StudentEnrolmentSystem:
    def _init_(self, db: Database, student: Dict[str, Any]):
        self.db = db
        self.student = student

    # ----------- Main Menu -----------
    def menu(self) -> None:
        while True:
            print("\n=== Subject Enrolment System ===")
            print("(e) Enrol subject")
            print("(r) Remove subject")
            print("(s) Show subjects")
            print("(c) Change password")
            print("(x) Exit")

            choice = (input("> ") or "").strip().lower()

            # Validate menu input for consistency across the app
            if not validate_menu_choice(choice, {"e", "r", "s", "c", "x"}):
                print("Invalid choice, please try again.")
                continue

            if choice == "e":
                self.enrol_subject()
            elif choice == "r":
                self.remove_subject()
            elif choice == "s":
                self.show_subjects()
            elif choice == "c":
                self.change_password()
            elif choice == "x":
                print("Exiting enrolment system...")
                break

    # ----------- Enrol Subject -----------
    def enrol_subject(self) -> None:
        subjects = self.student.get("subjects", [])
        if len(subjects) >= 4:
            print("You cannot enrol in more than four (4) subjects.")
            return

        new_subject = Subject([s["id"] for s in subjects])
        subjects.append(new_subject.to_dict())
        self.student["subjects"] = subjects

        self._update_student_stats()
        self.db.update_student(self.student)

        print(
            f"Enrolled in subject {new_subject.id} | "
            f"Mark: {new_subject.mark} | Grade: {new_subject.grade}"
        )

    # ----------- Remove Subject -----------
    def remove_subject(self) -> None:
        subjects = self.student.get("subjects", [])
        if not subjects:
            print("You are not enrolled in any subjects.")
            return

        sid = input("Enter Subject ID to remove: ").strip()
        if not sid:
            print("Invalid subject ID.")
            return

        new_list = [s for s in subjects if s["id"] != sid]
        if len(new_list) == len(subjects):
            print("Subject ID not found.")
            return

        self.student["subjects"] = new_list
        self._update_student_stats()
        self.db.update_student(self.student)
        print(f"Subject {sid} removed successfully.")

    # ----------- Show Subjects -----------
    def show_subjects(self) -> None:
        subjects = self.student.get("subjects", [])
        if not subjects:
            print("No subjects enrolled.")
            return

        print("\n=== Your Enrolled Subjects ===")
        for s in subjects:
            print(f"  Subject ID: {s['id']} | Mark: {s['mark']} | Grade: {s['grade']}")

        avg = self.student.get("average", 0.0)
        grade = self.student.get("grade", "Z")
        status = self.student.get("status", "FAIL")
        print(f"\nAverage Mark: {avg:.2f}")
        print(f"Overall Grade: {grade} | Status: {status}")

    # ----------- Change Password -----------
    def change_password(self) -> None:
        old = input("Enter current password: ").strip()
        if old != self.student.get("password"):
            print("Incorrect password.")
            return

        new_pw = input("Enter new password: ").strip()
        if not new_pw:
            print("Password cannot be empty.")
            return

        # Enforce shared password rule; reusing the same password is allowed
        if not is_valid_password(new_pw):
            print("Password must start with uppercase, have 5+ letters, and 3+ digits.")
            return

        self.student["password"] = new_pw
        self.db.update_student(self.student)
        print("Password updated successfully.")

    # ----------- Internal Helper -----------
    def _update_student_stats(self) -> None:
        """Recompute average/overall grade/status from current subjects."""
        subjects = self.student.get("subjects", [])
        if not subjects:
            self.student["average"] = 0.0
            self.student["grade"] = "Z"
            self.student["status"] = "FAIL"
            return

        # Ensure type safety for marks stored as strings/ints
        avg = sum(int(s["mark"]) for s in subjects) / len(subjects)
        self.student["average"] = round(avg, 2)
        self.student["grade"] = mark_to_grade(int(round(avg)))
        self.student["status"] = "PASS" if avg >= 50 else "FAIL"
