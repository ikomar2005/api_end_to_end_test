import requests
import json
import jsonpath
import mysql.connector


# __________________ Authorization API _____________________________________


# Signs in user into application as teacher
def test_sign_in_teacher():
    global API_URL, HEADER_TEACHER, PATH_DATA, HOST_DATABASE, PORT_DATABASE
    API_URL = "http://ask-stage.portnov.com/api/v1"
    PATH_DATA = "Testcases/JSON_DATA"
    HOST_DATABASE = ""
    PORT_DATABASE = ""
    test_url = API_URL + "/sign-in"
    file_in = open(PATH_DATA + "/teacher.json", "r")
    json_request = json.loads(file_in.read())
    file_in.close()
    response = requests.post(test_url, json=json_request)
    json_response = json.loads(response.text)
    teacher_token = "Bearer " + jsonpath.jsonpath(json_response, "token")[0]
    HEADER_TEACHER = {"Authorization": teacher_token}
    print("\n")
    print("Teacher_sign_in: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Signs in user into application as student
def test_sign_in_student():
    global HEADER_STUDENT, STUDENT_ID, STUDENT_EMAIL
    test_url = API_URL + "/sign-in"
    file_in = open(PATH_DATA + "/student.json", "r")
    json_request = json.loads(file_in.read())
    file_in.close()
    response = requests.post(test_url, json=json_request)
    json_response = json.loads(response.text)
    student_token = "Bearer " + jsonpath.jsonpath(json_response, "token")[0]
    HEADER_STUDENT = {"Authorization": student_token}
    STUDENT_EMAIL = jsonpath.jsonpath(json_request, "email")[0]
    STUDENT_ID = jsonpath.jsonpath(json_response, "user.id")[0]
    print("Student_sign_in: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Creates new user with STUDENT permission and sends verification email
def test_create_new_user():
    global NEW_USER_EMAIL
    test_url = API_URL + "/sign-up"
    file_in = open(PATH_DATA + "/new_user.json", "r")
    json_request = json.loads(file_in.read())
    file_in.close()
    NEW_USER_EMAIL = jsonpath.jsonpath(json_request, "email")[0]
    response = requests.post(test_url, headers=HEADER_TEACHER, json=json_request)
    print("New student created: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Activates account after creation
def test_activate_user():
    global NEW_USER_ID
    try:
        cnx = mysql.connector.connect(user="testuser", password="password", host=HOST_DATABASE,
                                  port=PORT_DATABASE, database="application")
        if cnx.is_connected():
            print("Connected to MySQL database host: "+HOST_DATABASE)
    except Error as e:
        print(e)
        return
    finally:
        cursor = cnx.cursor()
        query = "SELECT * FROM  users WHERE email = %(umail)s"
        cursor.execute(query, {"umail": NEW_USER_EMAIL})
        result = cursor.fetchall()
        cursor.close()
        cnx.close()
        NEW_USER_ID = result[0][0]
        user_code = result[0][6]
        test_url = API_URL + "/activate" + "/" + str(NEW_USER_ID) + "/" + user_code
        response = requests.get(test_url)
        print("New student activated: ", response.status_code)
        print("Time: ", response.elapsed)
        assert response.status_code == 200


# Submits request for password change
def test_forgot_password():
    test_url = API_URL + "/forgot-password"
    file_in = open(PATH_DATA + "/s_chng_psw.json", "r")
    json_request = json.loads(file_in.read())
    file_in.close()
    response = requests.post(test_url, headers=HEADER_STUDENT, json=json_request)
    print("Student forgot password: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Resets password after /forgot-password success
def test_reset_password():
    file_in = open(PATH_DATA + "/s_reset_psw.json", "r")
    json_request = json.loads(file_in.read())
    file_in.close()
    try:
        cnx = mysql.connector.connect(user="testuser", password="password", host=HOST_DATABASE,
                                  port=PORT_DATABASE, database="application")
        if cnx.is_connected():
            print("Connected to MySQL database host: "+HOST_DATABASE)
    except Error as e:
        print(e)
        return
    finally:
        cursor = cnx.cursor()
        query = "SELECT * FROM  users WHERE email = %(umail)s"
        cursor.execute(query, {"umail": STUDENT_EMAIL})
        result = cursor.fetchall()
        cursor.close()
        cnx.close()
        user_code = result[0][6]
        test_url = API_URL + "/reset-password" + "/" + str(STUDENT_ID) + "/" + user_code
        response = requests.post(test_url, headers=HEADER_STUDENT, json=json_request)
        print("Student reset password: ", response.status_code)
        print("Time: ", response.elapsed)
        assert response.status_code == 200


# __________________ Quiz API _____________________________________

# Returns list of all quizzes
def test_list_of_quizzes():
    test_url = API_URL + "/quizzes"
    response = requests.get(test_url, headers=HEADER_TEACHER)
    print("Get list of quizzes: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Creates new Quiz
def test_create_new_quiz():
    global QUIZ_ID
    test_url = API_URL + "/quiz"
    file_in = open(PATH_DATA + "/new_quiz.json", "r")
    json_request = json.loads(file_in.read())
    file_in.close()
    response = requests.post(test_url, headers=HEADER_TEACHER, json=json_request)
    json_response = json.loads(response.text)
    QUIZ_ID = jsonpath.jsonpath(json_response, "id")[0]
    print("Create new quiz: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Updates Quiz
def test_update_quiz():
    test_url = API_URL + "/quiz"
    file_in = open(PATH_DATA + "/update_quiz.json", "r")
    request = file_in.read()
    file_in.close()
    json_request = json.loads(request)
    json_request["id"] = str(QUIZ_ID)
    response = requests.put(test_url, headers=HEADER_TEACHER, json=json_request)
    print("Update quiz: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Deletes Quiz
def test_delete_quiz():
    test_url = API_URL + "/quiz" + "/" + str(QUIZ_ID)
    response = requests.delete(test_url, headers=HEADER_TEACHER)
    print("Delete quiz: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# __________________ Users API _____________________________________


# Returns list of all users
def test_list_of_users():
    test_url = API_URL + "/users"
    response = requests.get(test_url, headers=HEADER_TEACHER)
    print("Get list of users: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Changes user's name
def test_change_user_name():
    file_in = open(PATH_DATA + "/user_name.json", "r")
    request = file_in.read()
    file_in.close()
    request_json = json.loads(request)
    test_url = API_URL + "/users/change-name" + "/" + str(NEW_USER_ID)
    response = requests.put(test_url, headers=HEADER_TEACHER, json=request_json)
    print("Change name of user: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Changes user's group
def test_change_user_group():
    file_in = open(PATH_DATA + "/user_group.json", "r")
    request = file_in.read()
    file_in.close()
    request_json = json.loads(request)
    test_url = API_URL + "/users/change-name" + "/" + str(NEW_USER_ID)
    response = requests.put(test_url, headers=HEADER_TEACHER, json=request_json)
    print("Change group of user: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Changes user's role
def test_change_user_role():
    file_in = open(PATH_DATA + "/user_role.json", "r")
    request = file_in.read()
    file_in.close()
    request_json = json.loads(request)
    test_url = API_URL + "/users/change-name" + "/" + str(NEW_USER_ID)
    response = requests.put(test_url, headers=HEADER_TEACHER, json=request_json)
    print("Change of user role: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Deletes user
def test_delete_user():
    test_url = API_URL + "/users" + "/" + str(NEW_USER_ID)
    response = requests.delete(test_url, headers=HEADER_TEACHER)
    print("Delete user: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# __________________ Settings API _____________________________________


# Allows student user to change his/her name
def test_change_student_name():
    test_url = API_URL + "/settings/change-name"
    file_in = open(PATH_DATA + "/new_student_name.json", "r")
    request = file_in.read()
    file_in.close()
    request_json = json.loads(request)
    response = requests.post(test_url, headers=HEADER_STUDENT, json=request_json)
    print("Change student name: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Allows teacher user to change his/her name
def test_change_teacher_name():
    test_url = API_URL + "/settings/change-name"
    file_in = open(PATH_DATA + "/new_teacher_name.json", "r")
    request = file_in.read()
    file_in.close()
    request_json = json.loads(request)
    response = requests.post(test_url, headers=HEADER_TEACHER, json=request_json)
    print("Change teacher name: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Allows sudent user to change his/her password
def test_change_student_password():
    test_url = API_URL + "/settings/change-password"
    file_in = open(PATH_DATA + "/new_student_psw.json", "r")
    request = file_in.read()
    file_in.close()
    request_json = json.loads(request)
    response = requests.post(test_url, headers=HEADER_STUDENT, json=request_json)
    print("Change student password: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Allows teacher user to change his/her password
def test_change_teacher_password():
    test_url = API_URL + "/settings/change-password"
    file_in = open(PATH_DATA + "/new_teacher_psw.json", "r")
    request = file_in.read()
    file_in.close()
    request_json = json.loads(request)
    response = requests.post(test_url, headers=HEADER_TEACHER, json=request_json)
    print("Change teacher password: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# __________________ Assignment API _____________________________________

# Returns list of all assignments
def test_list_of_assignments():
    test_url = API_URL + "/assignments"
    response = requests.get(test_url, headers=HEADER_TEACHER)
    print("Get list of assignments: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Create quiz for new assignment
def test_new_quiz_for_assignment():
    global QUIZ_ID
    test_url = API_URL + "/quiz"
    file_in = open(PATH_DATA + "/new_quiz.json", "r")
    json_request = json.loads(file_in.read())
    file_in.close()
    response = requests.post(test_url, headers=HEADER_TEACHER, json=json_request)
    json_response = json.loads(response.text)
    QUIZ_ID = jsonpath.jsonpath(json_response, "id")[0]
    if response.status_code == 200:
        print("Quiz for assignment is created, status code: ", response.status_code)


# Creates new Assignment
def test_create_new_assignment():
    global ASSIGNMENT_ID, ASSIGNMENT_GROUP_ID
    test_url = API_URL + "/assignment"
    st_id = []
    st_id.append(int(STUDENT_ID))
    request_json = {"quizId": int(QUIZ_ID), "userIds": st_id}
    response = requests.post(test_url, headers=HEADER_TEACHER, json=request_json)
    json_response = json.loads(response.text)
    ASSIGNMENT_ID = jsonpath.jsonpath(json_response[0], "id")[0]
    ASSIGNMENT_GROUP_ID = jsonpath.jsonpath(json_response[0], "assignmentGroupID")[0]
    print("Create new assignment: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Returns list of all assignments that need to be completed (Student only)
def test_list_of_student_assignments():
    test_url = API_URL + "/my-assignments"
    response = requests.get(test_url, headers=HEADER_STUDENT)
    print("List of student assignments: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Submits assignment's result (Student only)
def test_submit_assignment_result():
    test_url = API_URL + "/submit-assignment"
    file_in = open(PATH_DATA + "/submit_assignment.json", "r")
    json_request = json.loads(file_in.read())
    file_in.close()
    json_request["assignmentId"] = int(ASSIGNMENT_ID)
    response = requests.post(test_url, headers=HEADER_STUDENT, json=json_request)
    print("Student submits assignment: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Grades assignment (teacher)
def test_grade_assignment():
    test_url = API_URL + "/assignment" + "/" + str(ASSIGNMENT_ID)
    file_in = open(PATH_DATA + "/assignment_result.json", "r")
    request = file_in.read()
    file_in.close()
    request_json = json.loads(request)
    response = requests.put(test_url, headers=HEADER_TEACHER, json=request_json)
    print("Teacher grades assignment: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Returns list of all submitted/graded assignments (student)
def test_list_of_graded_assignments():
    test_url = API_URL + "/my-grades"
    response = requests.get(test_url, headers=HEADER_STUDENT)
    print("List of graded assignments: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Deletes group of assignments
def test_delete_group_of_assignment():
    test_url = API_URL + "/assignment" + "/" + ASSIGNMENT_GROUP_ID
    response = requests.delete(test_url, headers=HEADER_TEACHER)
    print("Delete group of assignments: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200


# Deletes Quiz for assignment
def test_delete_quiz_for_assignment():
    test_url = API_URL + "/quiz" + "/" + str(QUIZ_ID)
    response = requests.delete(test_url, headers=HEADER_TEACHER)
    print("Delete quiz for assignment: ", response.status_code)
    print("Time: ", response.elapsed)
    assert response.status_code == 200
