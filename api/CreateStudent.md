**Create Student**
----
  Adds a student with the information provided in the JSON body of the request.

* **URL**

  /students/

* **Method:**

  `POST`
  
*  **URL Params**

   **Required:**
 
   None
   

* **Data Params**

    `{name:"John Doe", username: "username"}`

* **Success Response:**

  * **Code:** 201 CREATED <br />
    **Content:** `{id:"5cda791f5aec95bb5a5abd7c", name:"John Doe", username: "username"}`
 
* **Error Response:**

  * **Code:** 409 CONFLICT <br />
    **Content:** `{ error : "Conflict - The resource already exists"}`
    This is returned when a student with the given surname already exists

  OR

  * **Code:** 400 BAD REQUEST <br />
    **Content:** `{ error : "Bad request" }`
    
    
  OR

  * **Code:** 500 INTERNAL SERVER ERROR <br />
    **Content:** `{ error : "Internal Server Error" }`