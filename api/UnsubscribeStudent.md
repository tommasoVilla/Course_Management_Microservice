**Unsubscribe student from course**
----

    Cancel the student's subscription for the course
* **URL**

  /students/:student_username/courses/:course_id

* **Method:**

  `DELETE`
  
*  **URL Params**

   **Required:**
 
   `student_username=[string]`<br/>
   `course_id=[string]`
   
* **Data Params**

    None

* **Success Response:**

  * **Code:** 200 OK <br />
    **Content:** `{
    "courses": [
        "5cdc6d2339f578a97998a8d9",
        "5cdc6d7439f578a97998a8da",
        "5cdc6dac39f578a97998a8db",
        "5cdc6dfe39f578a97998a8dc"
    ],
    "id": "5cdfd0da04e5d52398f3d8f9",
    "name": "John Doe",
    "username": "student_username"
}` (This is the updated student)
 
* **Error Response:**

  * **Code:** 500 INTERNAL SERVER ERROR <br />
    **Content:** `{ error : "Internal Server Error" }`
    
  OR

  * **Code:** 404 NOT FOUND <br />
    **Content:** `{ error : "Student Not Found" }`
    This is returned where a student with the given username does not exist
    
  OR

  * **Code:** 404 NOT FOUND <br />
    **Content:** `{ error : "Course Not Found" }`
    This is returned where a course with the given id does not exist
     