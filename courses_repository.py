from bson import ObjectId
from pymongo.errors import PyMongoError

"""
This module provides functions that handle the interaction with courses persistence layer.
The persistence layer is a Mongo data-store.
"""


class CoursesRepositoryException(Exception):
    pass


def find_course_by_id(db_client, course_id):
    """
    Search for a course with the given course_id in the data store
    :param db_client: instance of MongoClient used to make requests to the data store
    :param course_id: id of the course the function is looking for in the data store
    :return: the course with the given id if a matching one exists, None otherwise
    """
    try:
        # Access to course_management db
        db = db_client.course_management
        # Access to courses collection
        courses = db.courses

        matching_course = courses.find_one({"_id": ObjectId(course_id)})
        if matching_course is None:
            return None
        matching_course['id'] = str(matching_course.pop('_id'))  # For JSON serialization
        return matching_course
    except PyMongoError:
        raise CoursesRepositoryException()


def find_course(db_client, by, string):
    """
    Find the courses matching with specified string. The given db_client is used to connect with data store
    :param db_client: instance of MongoClient used to make requests to the data store
    :param string: string represent the sequence to search
    :param by: string represent the field of course in which search the sequence.
        If type is "name" the courses are found by name. if type is "teacher" the courses are found by teacher.
    :return: the found courses, None if no one is found
    """
    try:

        # Access to course_management db
        db = db_client.course_management
        # Access to courses collection
        courses = db.courses

        # Find all courses contains string passing as parameter
        if by == "name":
            find_result = list(courses.find({'name': {'$regex': string, '$options': 'i'}}))
        else:
            strings = string.split("-")
            if len(strings) > 1:
                find_result = list(courses.find({'teacher': {'$regex': strings[0] + " " + strings[1], '$options': 'i'}}))
            else:
                find_result = list(courses.find({'teacher': {'$regex': string, '$options': 'i'}}))  # $options: i is for case-insensitive research

        if len(find_result) == 0:
            return None

        for item in find_result:
            item['id'] = str(item["_id"])
            item.pop("_id")  # For JSON serialization

        return find_result

    except PyMongoError:
        raise CoursesRepositoryException()


def find_courses_by_ids(db_client, id_list):
    """
    Find the courses with the id in the given id_list inside the data store
    :param db_client: instance of MongoClient used to make requests to the data store
    :param id_list: list of courses identifier
    :return: list of courses having the provided id
    """
    try:
        # Access to course_management db
        db = db_client.course_management
        # Access to courses collection
        courses = db.courses
        matching_courses = []
        for course_id in id_list:
            course_with_id = courses.find_one({"_id": ObjectId(course_id)})
            if course_with_id is not None:
                course_with_id['id'] = str(course_with_id.pop('_id'))  # For JSON serialization
                matching_courses.append(course_with_id)
        return matching_courses

    except PyMongoError:
        raise CoursesRepositoryException()


def add_course(db_client, course_dict):
    """
    Add the given course to the data store using the given db_client
    :param db_client: instance of MongoClient used to make requests to the data store
    :param course_dict: dictionary representing the course to be added to the data store
    :return: the added course, None if a conflict occurred
    """
    try:

        # Access to course_management db
        db = db_client.course_management
        # Access to courses collection
        courses = db.courses

        # Check if the course is in conflict with an existent one in the data store
        conflictual_course = courses.find_one({'name': course_dict['name'],
                                               'department': course_dict['department'],
                                               'teacher': course_dict['teacher'],
                                               'year': course_dict['year']})

        if conflictual_course is not None:
            return None

        # Make the insert
        insert_result = courses.insert_one(course_dict)

        if insert_result.inserted_id is None:
            raise CoursesRepositoryException()

        course_dict.pop('_id')
        course_dict['id'] = str(insert_result.inserted_id)  # For JSON serialization
        return course_dict

    except PyMongoError:
        raise CoursesRepositoryException()
