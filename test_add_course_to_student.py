import unittest

from bson import ObjectId
from pymongo import MongoClient

from app import app

mongo_client = MongoClient()


class TestAddCourseToStudent(unittest.TestCase):

    # To make the test a default student and a default course are stored into the db
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        db = mongo_client.course_management
        courses = db.courses
        courses.insert_one({"name": "corso",
                            "department": "dipartimento",
                            "teacher": "docente",
                            "year": "2019-2020",
                            "semester": 2,
                            "description": "descrizione",
                            "schedule": [{"day": "lun", "startTime": "09:00", "endTime": "10:30", "room": "A1"},
                                         {"day": "mar", "startTime": "10:30", "endTime": "11:30", "room": "C6"}]})
        courses.insert_one({"_id": ObjectId('aaaaaaaaaaaaaaaaaaaaaaaa'),
                                     "name": "corso_in_conflitto",
                                     "department": "dipartimento",
                                     "teacher": "docente",
                                     "year": "2019-2020",
                                     "semester": 2,
                                     "description": "descrizione",
                                     "schedule": [
                                         {"day": "lun", "startTime": "09:00", "endTime": "10:30", "room": "A1"},
                                         {"day": "mar", "startTime": "10:30", "endTime": "11:30", "room": "C6"}]})
        students = db.students
        students.insert_one({"name": "John Doe",
                             "username": "student_username",
                             "courses": [ObjectId('aaaaaaaaaaaaaaaaaaaaaaaa')]})

    # Testing standard case: the courses is added to the student
    def test_add_course_success(self):
        course_id = str(mongo_client.course_management.courses.find_one({"name": "corso"})['_id'])
        response = self.app.put('/course_management/api/v1.0/students/student_username/courses/' + course_id)
        self.assertEqual(200, response.status_code)

    # Testing append attempt of a course that is already in the user's list
    def test_conflict_course(self):
        response = self.app.put(
            '/course_management/api/v1.0/students/student_username/courses/aaaaaaaaaaaaaaaaaaaaaaaa')
        self.assertEqual(409, response.status_code)

    # Testing the following scenario: the user requires the update of a not-existing student
    def test_not_found_student(self):
        course_id = str(mongo_client.course_management.courses.find_one({"name": "corso"})['_id'])
        response = self.app.put('/course_management/api/v1.0/students/not_exist/courses/' + course_id)
        pass_condition = 404 == response.status_code and response.json['error'] == 'Student Not Found'
        self.assertEqual(True, pass_condition)

    # Testing the following scenario: the user requires to add a not-existing course
    def test_not_found_course(self):
        response = self.app.put(
            '/course_management/api/v1.0/students/student_username/courses/5cdc6dfe39f578a97998a8db')
        pass_condition = 404 == response.status_code and response.json['error'] == 'Course Not Found'
        self.assertEqual(True, pass_condition)

    # The data store is cleaned up after the execution of the test
    def tearDown(self):
        db = mongo_client.course_management
        courses = db.courses
        students = db.students
        courses.delete_one({"name": "corso"})
        courses.delete_one({"name": "corso_in_conflitto"})
        students.delete_one({"username": "student_username"})
