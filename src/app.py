__authors__ = ["shawkins", "Tsintsir", "sonph", "LeBat"]  # add yourself!

# internal (project libs)
from config import GITOLITE_ADMIN_PATH
from db import UsernameAlreadyTakenError, EmailAlreadyTakenError
from gitolite import GitoliteWrapper, UserDoesNotExistError, KeyDoesNotExistError, \
    CannotDeleteOnlyKeyError, KeyAlreadyExistsError
from db import  ClassDoesNotExistError, UrlNameAlreadyTakenError, DatabaseWrapper, ProjectDoesNotExistError

# base (python packages)

# external (pip packages)
from flask import Flask, jsonify
from flask import request
from sshpubkeys import InvalidKeyException

app = Flask(__name__)
app.debug = True  # TODO: unset this after release!


@app.route('/')
def hello_world():
    return jsonify({"hello": "world"})


@app.route('/<username>/ssh_keys/', methods=['GET'])
def list_ssh_keys(username):
    gw = GitoliteWrapper(GITOLITE_ADMIN_PATH)
    if not gw.user_exists(username):
        return jsonify({"error": "username not found!", "exception": None}), 404
    return jsonify(keys=gw.get_list_of_pretty_key_strings(username))


@app.route('/login/', methods=['POST'])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    dbw = DatabaseWrapper()
    result = dbw.login(username, password)
    if not result:
        return jsonify({"error": "bad login credentials!", "exception": None}), 400
    # TODO: authentication: return token from login
    return jsonify({"token": result}), 200


@app.route('/<username>/ssh_keys/', methods=['POST'])
def post_new_ssh_key(username):
    if False:  # TODO: ensure that username exists
        return jsonify({"error": "username does not exist"}), 404

    if False:  # TODO: ensure user is authed and is self
        return jsonify({"error": "Unauthorized"}), 401

    gw = GitoliteWrapper(GITOLITE_ADMIN_PATH)
    pkey_contents = request.form.get("pkey_contents")

    if not pkey_contents:
        return jsonify({"error": "No key was given!"}), 400

    try:
        pretty_key_hex = gw.add_pkey_to_user(username, pkey_contents)
        return jsonify(key_added=pretty_key_hex)
    except InvalidKeyException as e:
        return jsonify({"error": "Public key was invalid format", "exception": str(e)}), 400
    except KeyAlreadyExistsError as e:
        return jsonify({"error": "Public key already exists", "exception": str(e)}), 400
    except UserDoesNotExistError as e:
        return jsonify({"error": "username not found!", "exception": str(e)}), 404


@app.route('/<username>/ssh_keys/', methods=['DELETE'])
def remove_key_from_user(username):
    if False:  # TODO: ensure user is authed and is self
        return jsonify({"error": "Unauthorized"}), 401

    gw = GitoliteWrapper(GITOLITE_ADMIN_PATH)
    pkey = request.form.get("pkey")

    try:
        result = gw.remove_key_from_user_by_pretty_string(username, pkey)
    except KeyDoesNotExistError as e:
        return jsonify({"error": "Key does not exist for user!", "exception": str(e)}), 404
    except CannotDeleteOnlyKeyError as e:
        return jsonify({"error": "Can't delete the only key on the account!", "exception": str(e)}), 400
    if not result:
        return jsonify({"error": "Key was not found under user!", "exception": None}), 404
    return list_ssh_keys(username)


@app.route('/signup/', methods=['POST'])
def signup():
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")
    dbw = DatabaseWrapper()
    try:
        dbw.create_user(username, password,email)
    except UsernameAlreadyTakenError as e:
        return jsonify({"error": "Username is already taken!", "exception": str(e)}), 400
    except EmailAlreadyTakenError as e:
        return jsonify({"error": "Email is already taken!", "exception": str(e)}), 400
    result = dbw.login(username, password)
    return jsonify({"token": result}), 200


@app.route('/classes/')
def list_classes():
    dbw = DatabaseWrapper()
    return jsonify(classes=dbw.get_all_classes())


@app.route('/classes/', methods=["POST"])
def new_class():
    dbw = DatabaseWrapper()
    class_name = request.form.get("class_name")
    url_name = request.form.get("url_name")
    description = request.form.get("description")

    owner = "spencer"  # TODO: get currently logged in user
    try:
        c = dbw.create_class(url_name, class_name, description, owner)
        print c
        return jsonify(class_created=url_name)
    except UrlNameAlreadyTakenError as e:
        return jsonify({"error": "Url name was already taken!", "exception": str(e)}), 403


@app.route('/classes/<class_url>/projects/')
def list_projects(class_url):
    dbw = DatabaseWrapper()
    return jsonify(projects=dbw.get_all_projects_for_class(class_url))


@app.route('/classes/<class_url>/owner/')
def class_owner(class_url):
    dbw = DatabaseWrapper()
    try:
        class_obj = dbw.get_class_or_error(class_url)
        return jsonify(owner=class_obj["owner"])
    except ClassDoesNotExistError as e:
        return jsonify({"error": "class not found!", "exception": str(e)}), 404


@app.route('/classes/<class_url>/teachers/')
def class_teachers(class_url):
    dbw = DatabaseWrapper()
    try:
        class_obj = dbw.get_class_or_error(class_url)
        return jsonify(teachers=class_obj["teachers"])
    except ClassDoesNotExistError as e:
        return jsonify({"error": "class not found!", "exception": str(e)}), 404


@app.route('/classes/<class_url>/students/')
def class_students(class_url):
    dbw = DatabaseWrapper()
    try:
        class_obj = dbw.get_class_or_error(class_url)
        return jsonify(students=class_obj["students"])
    except ClassDoesNotExistError as e:
        return jsonify({"error": "class not found!", "exception": str(e)}), 404


@app.route('/classes/<class_url>/student/', methods=["POST"])
def add_student(class_url):
    dbw = DatabaseWrapper()
    student = request.form.get("username")

    try:
        dbw.add_student_to_class(class_url, student)
    except ClassDoesNotExistError as e:
        return jsonify({"error": "class not found!", "exception": str(e)}), 404
    except UserDoesNotExistError as e:
        return jsonify({"error": "username not found!", "exception": str(e)}), 404

    return jsonify(class_updated=dbw.get_class_or_error(class_url))


@app.route('/classes/<class_url>/teacher/', methods=["POST"])
def add_teacher(class_url):
    dbw = DatabaseWrapper()
    teacher = request.form.get("username")

    try:
        dbw.add_teacher_to_class(class_url, teacher)
    except ClassDoesNotExistError as e:
        return jsonify({"error": "class not found!", "exception": str(e)}), 404
    except UserDoesNotExistError as e:
        return jsonify({"error": "username not found!", "exception": str(e)}), 404

    return jsonify(class_updated=dbw.get_class_or_error(class_url))


@app.route('/classes/<class_url>/projects/<project_url>/owner/')
def get_project_owner(class_url, project_url):
    dbw = DatabaseWrapper()
    try:
        project_obj = dbw.get_project_or_error(class_url, project_url)
        return jsonify(owner=project_obj["owner"])
    except ClassDoesNotExistError as e:
        return jsonify({"error": "project not found!", "exception": str(e)}), 404


@app.route('/classes/<class_url>/projects/', methods=["POST"])
def new_project(class_url):
    dbw = DatabaseWrapper()
    project_name = request.form.get("project_name")
    url_name = request.form.get("url_name")
    description = request.form.get("description")
    team_based = request.form.get("team_based") in ["True", "true", "Yes", "yes"]
    max_size = int(request.form.get("max_members"))
    due_date = request.form.get("due_date")  # TODO: check formatting from js

    owner = "spencer"  # TODO: get currently logged in user

    try:
        dbw.create_project(url_name, project_name, description, class_url, team_based, due_date, owner, max_size)
        return jsonify(project_created=url_name)
    except UrlNameAlreadyTakenError as e:
        return jsonify({"error": "Url name was already taken!", "exception": str(e)}), 403
    except ClassDoesNotExistError as e:
        return jsonify({"error": "Class does not exist!", "exception": str(e)}), 404


@app.route('/classes/<class_url>/projects/<project_url>/due_date', methods=["POST"])
def new_project_due_date(class_url, project_url):
    dbw = DatabaseWrapper()
    due_date = request.form.get("date")
    return jsonify(project_updated=dbw.update_project_due_date(class_url, project_url, due_date))


@app.route('/classes/<class_name>/projects/<project_name>/make_submission/', methods=["POST"])
def make_submission(class_name, project_name):
    owner = request.form.get("owner")
    dbw = DatabaseWrapper()
    url_name = '/' + owner + '/submissions/' + project_name + '/'
    parent_url = '/' + class_name + '/projects/' + project_name + '/'
    try:
        dbw.create_submission(url_name, project_name, parent_url, owner)
        return jsonify(submission_made=url_name)
    except UrlNameAlreadyTakenError as e:
        return jsonify({"error": "Url name was already taken!", "exception": str(e)}), 403
    except ProjectDoesNotExistError as e:
        return jsonify({"error": "That project does not exist!", "exception": str(e)}), 404
    except ClassDoesNotExistError as e:
        return jsonify({"error": "Class does not exist!", "exception": str(e)}), 404


@app.route('/<username>/submissions/<submission_name>/contributors/', methods=['POST'])
def add_contributor(username, submission_name):
    new_contributor = request.form.get("username")
    dbw = DatabaseWrapper()
    try:
        dbw.add_contributor(username, submission_name, new_contributor)
        return jsonify(contributor_added=new_contributor)
    except StandardError as e:
        return jsonify({"error": "Placeholder error until exceptions are raised by the backend.", "exception": str(e)}), 404


@app.route('/<username>/submissions/<submission_name>/contributors/<removed_username>', methods=['DELETE'])
def remove_contributor(username, submission_name, removed_username):
    dbw = DatabaseWrapper()
    try:
        dbw.remove_contributor(username, submission_name, removed_username)
        return jsonify(contributor_removed=removed_username)
    except StandardError as e:
        return jsonify({"error": "Placeholder error until exceptions are raised by the backend.", "exception": str(e)}), 404


@app.route('/<username>/submissions/<submission_name>/contributors/', methods=['GET'])
def get_contributors(username, submission_name):
    dbw = DatabaseWrapper()
    return dbw.get_contributors(username, submission_name)

@app.route('/<username>/submissions/<submission_name>/source/<commit_path>/<filepath>')
def get_submission_file_or_directory(username, submission_name, commit_path, filepath):
    pass