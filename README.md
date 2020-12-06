# REST network

Social network that only uses HTTP.

## User

### Actions
* Create new user: 
    * **How:** Non authenticated `PUT /users/<username>`
    * **Data:** Body of request contains JSON 
      ```
      {
      "username": "<username>", 
      "email": "<email>", 
      "password": "<password>",
      "first_name": "<first_name>", // Optional
      "last_name": "<last_name>",   // Optional
      }
      ```
    * **Constraints:** _username_ not already in use
    * **Error:**  
