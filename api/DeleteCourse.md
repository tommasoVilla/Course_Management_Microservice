**Delete Course**
----
 Delete the course with the provided identifier
* **URL**

  /courses/:course_id

* **Method:**

  `DELETE`
  
*  **URL Params**

   **Required:**
 
   `course_id=[string]`
   

* **Data Params**

    None

* **Success Response:**

  * **Code:** 200 OK <br />
 
* **Error Response:**

  * **Code:** 404 NOT FOUND <br />
    **Content:** `{ error : "Course Not Found"}`
    
  OR

  * **Code:** 500 INTERNAL SERVER ERROR <br />
    **Content:** `{ error : "Internal Server Error" }`