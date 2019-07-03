import unittest
from pymongo import MongoClient

from app import app

mongo_client = MongoClient()


class TestGetExamBy(unittest.TestCase):

    # To make the test two default exams are added to the data store
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        db = mongo_client.course_management
        exams = db.exams
        exams.insert_one({"course": "IdCorso:re39ur32",
                          "call": 2,
                          "date": "21-03-2019",
                          "startTime": "10:30",
                          "room": "A1",
                          "expirationDate": "20-03-2019",
                          "students": []})
        exams.insert_one({"course": "IdCorso:re39ur32",
                          "call": 2,
                          "date": "21-04-2019",
                          "startTime": "11:30",
                          "room": "A1",
                          "expirationDate": "20-04-2019",
                          "students": []})

    # Testing the following scenario: the client searches for exams matching with the ones in data store
    def test_find_exam_by_course(self):
        response = self.app.get('/course_management/api/v1.0/exams/IdCorso:re39ur32')
        self.assertEqual(200, response.status_code)

    # Testing the following scenario: the client searches for exams not matching with the ones in data store
    def test_not_found_course(self):
        response = self.app.get('/course_management/api/v1.0/exams/notExistingId')
        self.assertEqual(404, response.status_code)

    # The data store is cleaned up after the execution of the test: the created exams are removed
    def tearDown(self):
        db = mongo_client.course_management
        exams = db.exams
        exams.delete_one({"course": "IdCorso:re39ur32",
                          "call": 1})
        exams.delete_one({"course": "IdCorso:re39ur32",
                          "call": 2})
