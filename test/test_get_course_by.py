import unittest
from pymongo import MongoClient

from app import app

mongo_client = MongoClient()


class TestGetCourseBy(unittest.TestCase):

    # To make the test two default courses are added to the data store
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        db = mongo_client.course_management
        courses = db.courses
        courses.insert_one({"name": "Analisi dei pattern sistemi",
                            "department": "dipartimento",
                            "teacher": "Tizio",
                            "year": "2019-2020",
                            "semester": 2,
                            "description": "descrizione",
                            "schedule": [{"day": "lun", "startTime": "09:00", "endTime": "10:30", "room": "A1"},
                                         {"day": "mar", "startTime": "10:30", "endTime": "11:30", "room": "C6"}]})
        courses.insert_one({"name": "Studio pattern",
                            "department": "dipartimento",
                            "teacher": "Doe",
                            "year": "2019-2020",
                            "semester": 2,
                            "description": "descrizione",
                            "schedule": [{"day": "lun", "startTime": "09:00", "endTime": "10:30", "room": "A1"},
                                         {"day": "mar", "startTime": "10:30", "endTime": "11:30", "room": "C6"}]})

    # Testing the following scenario: the user searches for a course by name and finds matching courses
    def test_find_course_by_name(self):
        response = self.app.get('/course_management/api/v1.0/courses/name/pattern')
        self.assertEqual(200, response.status_code)

    # Testing the following scenario: the user searches for a course by teacher and finds matching courses
    def test_find_course_by_teacher(self):
        response = self.app.get('/course_management/api/v1.0/courses/teacher/Doe')
        self.assertEqual(200, response.status_code)

    # Testing the following scenario: the user searches for a course by name but does not find matching courses
    def test_not_found_course(self):
        response = self.app.get('/course_management/api/v1.0/courses/name/zz')
        self.assertEqual(404, response.status_code)

    # Testing the following scenario: the user provides an invalid by clause in the url
    def test_bad_request(self):
        response = self.app.get('/course_management/api/v1.0/courses/other/a')
        self.assertEqual(400, response.status_code)

    def test_case_insensitive_research(self):
        response = self.app.get('/course_management/api/v1.0/courses/teacher/doe')
        self.assertEqual(200, response.status_code)

    # The data store is cleaned up after the execution of the test: the created courses are removed
    def tearDown(self):
        db = mongo_client.course_management
        courses = db.courses
        courses.delete_one({"name": "Analisi dei pattern sistemi"})
        courses.delete_one({"name": "Studio pattern"})
