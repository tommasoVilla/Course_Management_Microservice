"""
This module provides functions that handle the interaction with exams persistence layer.
The persistence layer is a Mongo data-store.
"""
from bson import ObjectId
from pymongo.errors import PyMongoError


class ExamsRepositoryException(Exception):
    pass


def serialize_exam(exam):
    """
    Convert the given exam (dictionary) in an other dictionary that can be "jsonified"
    :param exam:
    :return: the "jsonifiable" exam
    """
    exam['id'] = str(exam.pop('_id'))
    # if 'students' in exam:
    #     exam['students'] = list(map(str, exam['students'])) Uncomment if the student reference is its Mongo id
    return exam


def find_exam_by_course_id(db_client, course):
    """
    Find the exams of the course matching with specified id. The given db_client is used to connect with data store
    :param db_client: instance of MongoClient used to make requests to the data store
    :param course: id of the course of which search the exams
    :return: the found exams, None if no one is found
    """
    try:

        # Access to course_management db
        db = db_client.course_management
        # Access to exams collection
        exams = db.exams

        # Find all exams of the specified course
        find_result = list(exams.find({'course': course}))

        if len(find_result) == 0:
            return None

        matching_exams = list(map(serialize_exam, find_result))
        return matching_exams

    except PyMongoError:
        raise ExamsRepositoryException()


def find_exam_by_id(db_client, exam_id):
    """
        Find the exam with the given id.
        :param db_client: instance of MongoClient used to make requests to the data store
        :param exam_id: id of the exam to search
        :return: the found exam, None otherwise
    """
    try:
        # Access to course_management db
        db = db_client.course_management
        # Access to exams collection
        exams = db.exams

        matching_exam = exams.find_one({'_id': ObjectId(exam_id)})
        if matching_exam is None:
            return None
        return serialize_exam(matching_exam)
    except PyMongoError:
        raise ExamsRepositoryException()


def add_exam(db_client, exam_dict):
    """
    Add the given exam to the data store using the given db_client
    :param db_client: instance of MongoClient used to make requests to the data store
    :param exam_dict: dictionary representing the exam to be added to the data store
    :return: the added exam, None if a conflict occurred
    """
    try:

        # Access to course_management db
        db = db_client.course_management
        # Access to exams collection
        exams = db.exams

        # Check if the exam is in conflict with an existent one in the data store
        conflictual_exam = exams.find_one({'course': exam_dict['course'],
                                           'call': exam_dict['call']})

        if conflictual_exam is not None:
            return None

        # Make the insert
        insert_result = exams.insert_one(exam_dict)

        if insert_result.inserted_id is None:
            raise ExamsRepositoryException()

        return serialize_exam(exam_dict)

    except PyMongoError:
        raise ExamsRepositoryException()


def is_valid_reservation(db_client, exam_dict, student_dict):
    """
    Checks if the student is registered to the course. If this is not the case, he/she won't be allowed to reserve the exam
    :param db_client: instance of MongoClient used to make requests to the data store
    :param exam_dict:
    :param student_dict:
    :return: True or False
    """
    try:
        # Access to course_management db
        db = db_client.course_management
        #
    except PyMongoError:
        raise ExamsRepositoryException()

def add_student_to_exam(db_client, exam_dict, student_dict):
    """
    Reserve the exam for the given student
    :param db_client:
    :param exam_dict: exam to update
    :param student_dict: student to add
    :return: the updated exam, None in case of student already registered
    """

    try:
        # Access to course_management db
        db = db_client.course_management
        # Access to exams collection
        exams = db.exams
        # Check if the student is already registered to the exam
        if 'students' in exam_dict:
            exam_students = exam_dict['students']
            if student_dict['username'] in exam_students:
                return None
        # Add the student
        result = exams.update_one({"_id": ObjectId(exam_dict['id'])},
                                  {"$push": {"students": student_dict['username']}})
        if result.modified_count != 1:  # Something unexpected went wrong
            raise ExamsRepositoryException()
        updated_exam = exams.find_one({"_id": ObjectId(exam_dict['id'])})
        return serialize_exam(updated_exam)
    except PyMongoError:
        raise ExamsRepositoryException()
