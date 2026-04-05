"""
Data Manager Module
Handles reading and writing local student profile files.
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class DataManager:
    """Manages local storage of student profiles."""

    def __init__(self, students_dir: str = "students", plans_dir: str = "plans"):
        """
        Initialize the DataManager.

        Args:
            students_dir: Directory where student JSON files are stored
            plans_dir: Directory where lesson plans are saved
        """
        self.students_dir = Path(students_dir)
        self.students_dir.mkdir(exist_ok=True)

        self.plans_dir = Path(plans_dir)
        self.plans_dir.mkdir(exist_ok=True)

    def get_student_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load a student profile from disk.

        Args:
            name: Student's name (case-insensitive)

        Returns:
            Dictionary containing student profile data, or None if not found
        """
        # Try to find the file (case-insensitive)
        for file_path in self.students_dir.glob("*.json"):
            if file_path.stem.lower() == name.lower():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)

        return None

    def save_student_profile(self, profile: Dict[str, Any]) -> bool:
        """
        Save a student profile to disk.

        Args:
            profile: Dictionary containing student profile data

        Returns:
            True if successful, False otherwise
        """
        try:
            name = profile.get('name')
            if not name:
                return False

            file_path = self.students_dir / f"{name}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Error saving profile: {e}")
            return False

    def list_students(self) -> list[str]:
        """
        Get a list of all student names.

        Returns:
            List of student names
        """
        return [f.stem for f in self.students_dir.glob("*.json")]

    def student_exists(self, name: str) -> bool:
        """
        Check if a student profile exists.

        Args:
            name: Student's name (case-insensitive)

        Returns:
            True if profile exists, False otherwise
        """
        return self.get_student_profile(name) is not None

    def save_lesson_plan(self, student_name: str, content: str) -> str:
        """
        Save a lesson plan to disk.

        Args:
            student_name: Name of the student
            content: Markdown content of the lesson plan

        Returns:
            Success message with the file path, or error message
        """
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{student_name}_{timestamp}.md"
            file_path = self.plans_dir / filename

            # Write the content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"Success: Saved to plans/{filename}"
        except Exception as e:
            return f"Error: Failed to save lesson plan: {e}"

    def add_lesson_log(self, student_name: str, topic: str, notes: str) -> bool:
        """
        Appends a new lesson entry to a student's lesson_history.

        Args:
            student_name: The name of the student.
            topic: The topic taught in the lesson.
            notes: Performance notes for the student.

        Returns:
            True if the log was added successfully, False otherwise.
        """
        profile = self.get_student_profile(student_name)
        if not profile:
            return False

        # Ensure 'lesson_history' is a list
        if 'lesson_history' not in profile or not isinstance(profile['lesson_history'], list):
            profile['lesson_history'] = []

        # Create the new lesson entry
        new_lesson = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "topic_taught": topic,
            "student_performance_notes": notes
        }

        # Append the new lesson
        profile['lesson_history'].append(new_lesson)

        # Save the updated profile
        return self.save_student_profile(profile)

