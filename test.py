import requests
import json
"""
-Crete users
-Change one username
-Change password
-Change First name
-Change Last name

-Follow another user
-View followed user
-View user that followed another one
-Chech if fields are updated

-Create post
-View post
-View user, check if post number updated
-Check user posts site
-Delete post

-Delete all users
-Check if everything is like before
"""

def request_json(url, auth):
    "http://localhost:8000/users"
    request = requests.get(url, auth=auth, headers={'Accept': 'application/json; indent=2'})
    return json.loads(request.content.decode('utf-8'))

def decode_content(request):
    return request.content.decode('utf-8')


def get_users():
    return json.loads(requests.get("http://localhost:8000/users", auth=("kookie", "password")).content.decode("utf-8"))


def get_posts(user=None):
    if user:
        return json.loads(requests.get(f"http://localhost:8000/posts/{user}", auth=("kookie", "password")).content.decode("utf-8"))
    else:
        return json.loads(requests.get("http://localhost:8000/posts", auth=("kookie", "password")).content.decode("utf-8"))


def get_user(username):
    user_list = list(filter(lambda user: user['user']['username'] == username, get_users()))
    if len(user_list) == 1:
        return user_list[0]
    return None


def create_users():
    # Create user brian
    print("Creating user brian")
    request = requests.put("http://localhost:8000/users/brian", data={"username": "brian", "email": 'brian@gmail.com', "password": "password", "first_name": "Brian", "last_name": "May"})
    assert request.status_code == 201, f"Error creating user: {decode_content(request)}"
    assert get_user("brian"), "User does not exist"

    # Create user freddie
    print("Creating user freddie")
    request = requests.put("http://localhost:8000/users/freddie", data={"username": "freddie", "email": 'freddie@gmail.com', "password": "password"})
    assert request.status_code == 201, f"Error creating user: {decode_content(request)}"
    assert get_user("freddie"), "User does not exist"


def delete_user(user):
    # Delete users freddie and brian
    request = requests.delete(f"http://localhost:8000/users/{user}", auth=(user, "password"))
    assert request.status_code == 200, f"Error deleting user: {decode_content(request)}"


def change_user():
    print("Checking freddies name")
    freddie = get_user("freddie")
    assert len(freddie["user"]['first_name']) == 0, "Freddie has name!"

    print("Changing first name of freddie")
    request = requests.put("http://localhost:8000/users/freddie", auth=("freddie", "password"), data={"first_name": "Freddie"})
    assert request.status_code == 200, f"Error changing user: {decode_content(request)}"

    freddie = get_user("freddie")
    assert freddie["user"]['first_name'] == "Freddie", "Freddie did not change name!"

    print("Changing last name of freddie")
    request = requests.put("http://localhost:8000/users/freddie", auth=("freddie", "password"), data={"last_name": "Mercury"})
    assert request.status_code == 200, f"Error changing user: {decode_content(request)}"

    freddie = get_user("freddie")
    assert freddie["user"]['last_name'] == "Mercury", "Freddie did not change last name!"

    print("Changing freddies password")
    request = requests.put("http://localhost:8000/users/freddie", auth=("freddie", "password"), data={"password": "pass"})
    assert request.status_code == 200, f"Password did not change: {decode_content(request)}"

    print("Changing freddies password")
    request = requests.put("http://localhost:8000/users/freddie", auth=("freddie", "pass"), data={"password": "password"})
    assert request.status_code == 200, f"Password did not change: {decode_content(request)}"

    print("Trying to change username to brian")
    request = requests.put("http://localhost:8000/users/freddie", auth=("freddie", "password"), data={"username": "brian"})
    assert request.status_code == 400, f"Username changed: {decode_content(request)}"


def follow_user():
    print("Checking if freddie is following anyone")
    freddie = get_user("freddie")
    assert len(freddie["following"]) == 0, "Follows a ghost!"

    print("freddie starts following brian")
    request = requests.put("http://localhost:8000/follow/brian", auth=("freddie", "password"))
    assert request.status_code == 200, f"Error changing user: {decode_content(request)}"

    print("Checking if freddie is following anyone")
    freddie = get_user("freddie")
    assert len(freddie["following"]) == 1 and freddie["following"][0] == 'http://localhost:8000/users/brian', "Freddie is not following brian!"
    assert len(freddie["followers"]) == 0, "Freddie has followers!"

    print("Checking if brian has followers")
    brian = get_user("brian")
    assert len(brian["followers"]) == 1 and brian["followers"][0] == 'http://localhost:8000/users/freddie', "Freddie is not following brian!"
    assert len(brian["following"]) == 0, "Brian is following someone!"

    print("Deleting brian")
    delete_user('brian')

    freddie = get_user("freddie")
    assert len(freddie["followers"]) == 0, "Freddie is following a ghost!"


def create_posts():
    'curl - X POST - u randy: password - d "Mamma, I killed a man" http: // localhost: 8000 / post'
    print("Checking if freddie has a post")
    posts = get_posts("freddie")
    assert len(posts) == 0, "Freddie has posted something"

    print("freddie creates a post")
    request = requests.post("http://localhost:8000/post", auth=("freddie", "password"), data="Mamma, I killed a man!")
    assert request.status_code == 201, f"Error posting user: {decode_content(request)}"

    print("Checking if freddie has a post")
    posts = get_posts("freddie")
    assert len(posts) == 1, "Freddies post doesn't exist!"

    print("freddie creates a second post")
    request = requests.post("http://localhost:8000/post", auth=("freddie", "password"), data="Put a gun against his head")
    assert request.status_code == 201, f"Error posting user: {decode_content(request)}"

    print("Checking if freddie has a post")
    posts = get_posts("freddie")
    assert len(posts) == 2, "Freddies second post doesn't exist!"

    to_delete = posts[1]["id"]

    print("freddie deletes the second post")
    request = requests.delete(f"http://localhost:8000/posts/{to_delete}", auth=("freddie", "password"))
    assert request.status_code == 200, f"Error posting user: {decode_content(request)}"

    print("Checking if the second post was deleted")
    posts = get_posts("freddie")
    assert len(posts) == 1, "Freddies second post doesn't exist!"


users = get_users()
# Delete users if they are present
usernames = [ user['user']['username'] for user in users]
to_delete = ['freddie', 'brian']

for user in usernames:
    if user in to_delete:
        delete_user(user)


begin_state_users = get_users()
begin_state_posts = get_posts()

create_users()
change_user()
follow_user()
create_posts()
print("Deleting freddie")
delete_user('freddie')
end_state_users = get_users()
end_state_posts = get_posts()

# Check if begin and end state are the same
assert begin_state_users == end_state_users, "Users state is not back to old"
assert begin_state_posts == end_state_posts, "Posts state is not back to old"



