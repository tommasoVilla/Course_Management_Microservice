import unittest
from pymongo import MongoClient

from app import app

mongo_client = MongoClient()


class TestStudentCreation(unittest.TestCase):

    # To make the test a default student is added to the data store
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        db = mongo_client.course_management
        students = db.students
        students.insert_one({"name": "student", "username": "conflict"})

    # Testing standard case: an user complete the student creation
    def test_insert_course(self):
        student = {"name": "test", "username": "not_conflict"}

        response = self.app.post('/course_management/api/v1.0/students', json=student)
        self.assertEqual(201, response.status_code)

    # Testing creation attempt of a student that is in conflict with then one already in the data store
    def test_conflict_course(self):
        conflict_student = {"name": "test", "username": "conflict"}

        response = self.app.post('/course_management/api/v1.0/students', json=conflict_student)
        self.assertEqual(409, response.status_code)

    # Testing forwarding of a request with lacking fields (namely username is empty)
    def test_bad_request(self):
        bad_student = {"name": "not valid"}
        response = self.app.post('/course_management/api/v1.0/students', json=bad_student)
        self.assertEqual(400, response.status_code)

    # The data store is cleaned up after the execution of the test: the created students are removed
    def tearDown(self):
        db = mongo_client.course_management
        students = db.students
        students.delete_one({"name": "student"})
        students.delete_one({"name": "test"})
