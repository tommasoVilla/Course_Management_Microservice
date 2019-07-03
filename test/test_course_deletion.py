import unittest

from bson import ObjectId
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
        courses.insert_one({"_id": ObjectId("aaaaaaaaaaaaaaaaaaaaaaaa"),
                            "name": "corso",
                            "department": "dipartimento",
                            "teacher": "docente",
                            "year": "2019-2020",
                            "semester": 2,
                            "description": "descrizione",
                            "schedule": [{"day": "lun", "startTime": "09:00", "endTime": "10:30", "room": "A1"},
                                         {"day": "mar", "startTime": "10:30", "endTime": "11:30", "room": "C6"}]})

    # Testing standard case: an user complete the course deletion
    def test_delete_course(self):
        delete_response = self.app.delete('/course_management/api/v1.0/courses/aaaaaaaaaaaaaaaaaaaaaaaa',)
        get_response = self.app.get('/course_management/api/v1.0/courses/name/corso')
        pass_condition = delete_response.status_code == 200 and get_response.status_code == 404
        self.assertEqual(True, pass_condition)
