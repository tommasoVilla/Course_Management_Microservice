import unittest
from pymongo import MongoClient

from app import app

mongo_client = MongoClient()


class TestCourseCreation(unittest.TestCase):

    # To make the test a default course is added to the data store
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

    # Testing standard case: an user complete the course creation
    def test_insert_course(self):
        course = {"name": "test",
                  "department": "dipartimento",
                  "teacher": "docente",
                  "year": "2019-2020",
                  "semester": 1,
                  "description": "descrizione",
                  "schedule": [{"day": "mer", "startTime": "09:00", "endTime": "10:30", "room": "A1"},
                               {"day": "gio", "startTime": "10:30", "endTime": "11:30", "room": "C6"}]}

        response = self.app.post('/course_management/api/v1.0/courses', json=course)
        self.assertEqual(201, response.status_code)

    # Testing creation attempt of a course that is in conflict with the one already in the data store
    def test_conflict_course(self):
        conflict_course = {"name": "corso",
                           "department": "dipartimento",
                           "teacher": "docente",
                           "year": "2019-2020",
                           "semester": 1,
                           "description": "descrizione-altra",
                           "schedule": [{"day": "mer", "startTime": "09:00", "endTime": "10:30", "room": "A1"},
                                        {"day": "gio", "startTime": "10:30", "endTime": "11:30", "room": "C6"}]}

        response = self.app.post('/course_management/api/v1.0/courses', json=conflict_course)
        self.assertEqual(409, response.status_code)

    # Testing forwarding of a request with lacking fields (specifically schedule is empty)
    def test_bad_request(self):
        bad_course = {"name": "corso non valido",
                      "department": "dipartimento",
                      "teacher": "docente",
                      "year": "2019-2020",
                      "semester": 1,
                      "description": "descrizione",
                      "schedule": []}
        response = self.app.post('/course_management/api/v1.0/courses', json=bad_course)
        self.assertEqual(400, response.status_code)

    # The data store is cleaned up after the execution of the test: the created courses are removed
    def tearDown(self):
        db = mongo_client.course_management
        courses = db.courses
        courses.delete_one({"name": "corso"})
        courses.delete_one({"name": "test"})
