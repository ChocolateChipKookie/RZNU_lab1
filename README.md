# REST network

Social network that only uses HTTP.

## User

### Actions
* #### Create new user: 
  * **How:** Non authenticated `PUT /users/<username>`
  * **Who:**
    * Anyone (not authenticated)
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
  * **Constraints:**
    * **_username_** not already in use
    * **_username_** has to be alphanumeric
    * **_username_** cannot be only a number
    * **_email_** not already in use
  * **Possible errors:** 
    * **_username_** in json and url don't match
    * **_username_** contains non-alphanumeric symbols
    * **_username_** is a number
    * **_username_** already in use
    * **_email_** already in use
  * **Example**:
    ```
    curl -X PUT -H "Content-Type: application/json" -d '{"username":"randy","password":"pass","first_name":"Randy", "last_name":"Randić","email":"rrandic@gmail.com"}' http://localhost:8000/users/randy
    ```

* #### Update user data: 
  * **How:** Authenticated `PUT /users/<username>`
  * **Who:**
    * **user** that wants to edit his data
    * **superuser** that wants to edit any users data
    * **admin** that wants to give/revoke superuser rights
  * **Data:** Body of request contains JSON with only one of the following parameters
    ```
    {
    "username": "<username>",
    "email": "<email>",
    "password": "<password>",
    "first_name": "<first_name>",
    "last_name": "<last_name>",
    "superuser": True/False
    }
    ```
  * **Constraints:**
    * **_username_** not already in use 
    * **_username_** has to be alphanumeric
    * **_username_** cannot be only a number
    * **_email_** not already in use
    * **_superuser_** status can only be changed by **admin**
  * **Possible errors:** 
    * Request is not authenticated
    * **user** with given username doesn't exist
    * New **_username_** contains non-alphanumeric symbols
    * New **_username_** is a number
    * New **_username_** already in use
    * New **_email_** already in use
    * Permission denied (when trying to modify options of another **user** without superuser privileges)
    * Permission denied (when non **admin** is trying to modify **_superuser_**)
    * **admin** superuser status cannot be updated
  * **Example**:
    ```
    curl -X PUT -u randy:pass -H "Content-Type: application/json" -d '{"password":"password"}' http://localhost:8000/users/randy
    ```
      
* #### Delete user: 
  * **How:** Authenticated `DELETE /users/<username>`
  * **Who:**
    * **user** that wants to delete his account
    * **superuser** that wants to delete any **user** account except for other **superuser**
    * **admin** that wants to delete any account except **admin**
  * **Constraints:** 
    * **_username_** has to exist
    * **_username_** has match to **user** username if the **user** doesn't have superuser privileges
  * **Possible errors:** 
    * Request is not authenticated
    * **user** tries to delete another **user**
    * **admin** cannot be deleted
    * **superuser** cannot be deleted by anyone except **admin**
    * **user** does not exist
  * **Example**:
    ```
    curl -X DELETE -u randy:password http://localhost:8000/users/randy
    ```

* #### List users:
  * **How:** Authenticated `GET /users`
  * **Who:**
    * Anyone
  * **Data:** No additional data required
  * **Example**:
    ```
    curl -X GET -u randy:password -H 'Accept: application/json; indent=2' http://localhost:8000/users
    ```
  
* #### View user:
  * **How:** `GET /users/<username>`
  * **Who:**
    * Anyone who wants to view user
  * **Possible errors:**
    * **user** does not exist
  * **Example**:
    ```
    curl -X GET -H "Accept: application/json; indent=2" http://localhost:8000/users/kookie
    ```

* #### Follow user:
  * **How:** Authenticated `PUT /follow/<username>`
  * **Who:**
    * Any **user** that wants to follow another **user**
    * **users** without profile (exg. **admin**) cannot follow anyone
  * **Constraints:**
    * **_username_** must exist
  * **Possible errors:** 
    * **_request_** must be authenticated
    * **user** cannot follow himself
    * Pure **user** (without profile) cannot follow anyone
    * **user** to follow must exist
    * Cannot follow **user** twice
  * **Example**:
    ```
    curl -X PUT -u kookie:password http://localhost:8000/follow/randy
    ```
    
* #### Unfollow user:
  * **How:** Authenticated `DELETE /follow/<username>`
  * **Who:**
    * Any **user** that wants to unfollow another **user**
    * **users** without profile (exg. **admin**) cannot unfollow anyone as they can't have follow relationships
  * **Constraints:**
    * **_username_** must be of a **user** that you follow
  * **Possible errors:** 
    * **_request_** must be authenticated
    * Pure **user** (without profile) cannot unfollow anyone
    * Cannot unfollow **user** you don't follow
  * **Example**:
    ```
    curl -X DELETE -u kookie:password http://localhost:8000/follow/randy
    ```

## Posts

### Actions
* #### Create new post: 
  * **How:** Authenticated `POST /post`
  * **Who:**
    * **user** who wants to post something
    * **users** without profile (exg. admin) cannot post
  * **Data:** Body of request contains the plain text **_post_** content
  * **Constraints:**
    * **_post_** length is less or equal to 256 bytes
  * **Possible errors:** 
    * **post** too long (you will get informed about the length of the post)
    * **user** is pure user and does not have a profile (for example admin)
  * **Example**:
    ```
    curl -X POST -u randy:password -d "Mamma, I killed a man" http://localhost:8000/post
    ```

* #### View all posts: 
  * **How:** Authenticated `GET /posts`
  * **Who:**
    * Admin
  * **Possible errors:**
    * **user** doesn't have permission to view all posts
  * **Example**:
    ```
    curl -X GET -u admin:password -H "Accept: application/json; indent=2" http://localhost:8000/posts
    ```

* #### View a post: 
  * **How:** `GET /posts/<id>`
  * **Who:**
    * Anyone that wants to see a post
  * **Possible errors:**
    * **post** with given **_id_** does not exist
  * **Example**:
    ```
    curl -X GET -H "Accept: application/json; indent=2" http://localhost:8000/posts/2
    ```
  
* #### View all posts by a user: 
  * **How:** `GET /posts/<username>`
  * **Who:**
    * Anyone that wants to see the post history of the user
  * **Possible errors:**
    * **user** with given **_username_** does not exist
  * **Example**:
    ```
    curl -X GET -H "Accept: application/json; indent=2" http://localhost:8000/posts/2
    ```

* #### Delete a post: 
  * **How:** `DELETE /posts/<id>`
  * **Who:**
    * **user** that wants to delete his post
    * **superuser** that wants to delete any **user** post
  * **Constraints:** 
    * **post** **_id_** has to exist
    * **post** can only be deleted by user that created it or superuser
  * **Possible errors:** 
    * Request is not authenticated
    * **user** tries to delete another **user** post
    * **post** does not exist
  * **Example**:
    ```
    curl -X DELETE -u kookie:password  http://localhost:8000/posts/6
    ```
  