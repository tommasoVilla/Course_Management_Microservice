import unittest

from bson import ObjectId
from pymongo import MongoClient

from app import app

mongo_client = MongoClient()


class TestGetStudentCourses(unittest.TestCase):

    # To make the test two default courses and two default students are added to the data store
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        db = mongo_client.course_management
        courses = db.courses
        students = db.students
        students.insert_one({"username": "student_with_courses",
                             "name": "John Doe"})
        insert_result = courses.insert_one({"name": "Corso1",
                                            "department": "Dipartimento1",
                                            "teacher": "John Doe",
                                            "year": "2019-2020",
                                            "semester": 1,
                                            "description": "Descrizione1",
                                            "schedule": [
                                                {"day": "lun", "startTime": "09:00", "endTime": "10:30", "room": "A1"},
                                                {"day": "mar", "startTime": "10:30", "endTime": "11:30",
                                                 "room": "C6"}]})
        course_id = insert_result.inserted_id
        students.update_one({"username": "student_with_courses"},
                            {"$push": {"courses": ObjectId(course_id)}})
        insert_result = courses.insert_one({"name": "Corso2",
                                            "department": "Dipartimento2",
                                            "teacher": "John Doe",
                                            "year": "2019-2020",
                                            "semester": 2,
                                            "description": "Descrizione2",
                                            "schedule": [
                                                {"day": "lun", "startTime": "09:00", "endTime": "10:30", "room": "A1"},
                                                {"day": "mer", "startTime": "10:30", "endTime": "11:30",
                                                 "room": "C8"}]})
        course_id = insert_result.inserted_id
        students.update_one({"username": "student_with_courses"},
                            {"$push": {"courses": ObjectId(course_id)}})
        students.insert_one({"username": "student_without_courses",
                             "name": "Marco Rossi",
                             "courses": []})

    # Testing the following scenario: the client searches for the courses which the student is subscribed to and finds them
    def test_find_student_courses(self):
        response = self.app.get('/course_management/api/v1.0/courses/students/student_with_courses')
        self.assertEqual(200, response.status_code)

    # Testing the following scenario: the client searches for the courses which the student is subscribed to but the student
    # does not attend any course
    def test_find_course_not_found(self):
        response = self.app.get('/course_management/api/v1.0/courses/students/student_without_courses')
        pass_condition = 404 == response.status_code and response.json['error'] == 'Courses Not Found'
        self.assertEqual(True, pass_condition)

    # Testing the following scenario: the client searches for the courses of a student that does not exist
    def test_not_found_student(self):
        response = self.app.get('/course_management/api/v1.0/courses/students/not_existent_student')
        pass_condition = 404 == response.status_code and response.json['error'] == 'Student Not Found'
        self.assertEqual(True, pass_condition)

    # The data store is cleaned up after the execution of the test: the created courses and students are removed
    def tearDown(self):
        db = mongo_client.course_management
        courses = db.courses
        students = db.students
        courses.delete_one({"name": "Corso1"})
        courses.delete_one({"name": "Corso2"})
        students.delete_one({"username": "student_with_courses"})
        students.delete_one({"username": "student_without_courses"})
