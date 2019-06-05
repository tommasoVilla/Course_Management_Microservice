**Create Course**
----
  Adds a exam with the information provided in the JSON body of the request.

* **URL**

  /exams/

* **Method:**

  `POST`
  
*  **URL Params**

   **Required:**
 
   None
   

* **Data Params**

    `{course: "IdCourse", call: 2, date: "21-03-2019", startTime: "10:30", room: "A1",
	  expirationDate: "18-03-2019"}`

* **Success Response:**

  * **Code:** 201 CREATED <br />
    **Content:** `{ id: "5ce0165fe2c5c2136899fad5", course: "IdCourse", 
                    call: 2, date: "21-03-2019", startTime: "10:30",
                    room: "A1", expirationDate: "18-03-2019", students: []}`
 
* **Error Response:**

  * **Code:** 409 CONFLICT <br />
    **Content:** `{ error : "Conflict - The resource already exists"}`
    This is returned when a exam with the same given name and call exists

  OR

  * **Code:** 400 BAD REQUEST <br />
    **Content:** `{ error : "Bad request" }`
    
    
  OR

  * **Code:** 500 INTERNAL SERVER ERROR <br />
    **Content:** `{ error : "Internal Server Error" }`