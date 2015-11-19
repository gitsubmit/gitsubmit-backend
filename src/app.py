__authors__ = ["shawkins", "Tsintsir", "sonph", "LeBat"]  # add yourself!

# internal (project libs)
from security import crossdomain, basic_auth
from config import GITOLITE_ADMIN_PATH, DATABASE_PORT, STATIC_REPOS_ROOT
from db import UsernameAlreadyTakenError, EmailAlreadyTakenError, SubmissionDoesNotExistError
from git_browser import GitRepo
from gitolite import GitoliteWrapper, UserDoesNotExistError, KeyDoesNotExistError, \
    CannotDeleteOnlyKeyError, KeyAlreadyExistsError
from db import  ClassDoesNotExistError, UrlNameAlreadyTakenError, DatabaseWrapper, ProjectDoesNotExistError

# base (python packages)
from email.utils import parseaddr

# external (pip packages)
from flask import Flask, jsonify, request, Response, g
from sshpubkeys import InvalidKeyException

app = Flask(__name__)
app.debug = True  # TODO: unset this after release!


# note: this is unrouted
def configured_main(custom_gitolite_path, custom_repository_root_path, database_port):
    """ For testing versions of the API, we can point to a different gitolite admin directory, and a different database.
    Note that if this is not called (instead, gunicorn is invoked with app:app) then all defaults remain.

    :param custom_gitolite_path: path to local git instance of gitolite
    :param database_port: integer of port where mongodb is served
    :return: wsgi app instance
    """

    # first, set these attributes as global, so that in later uses, we get THESE versions
    global GITOLITE_ADMIN_PATH, DATABASE_PORT, STATIC_REPOS_ROOT
    GITOLITE_ADMIN_PATH = custom_gitolite_path
    DATABASE_PORT = database_port
    STATIC_REPOS_ROOT = custom_repository_root_path

    # gunicorn requires that whatever method we call returns the wsgi app, so:
    return app


# note: this is unrouted
def get_json_data():
    if len(request.form) > 0:  # we got form data
        return request.form
    else:  # hopefully, we got json. If not, this will raise a 400 error for us
        json_attempt = request.get_json(force=True)
    return json_attempt


# note: this is unrouted
def get_current_logged_in_user():
    token = getattr(g, 'token', dict())
    return token.get('username', None)


@app.route('/', methods=['GET', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def hello_world():
    print get_current_logged_in_user()
    return jsonify({"hello": "world"})


@app.route('/testpost/', methods=["POST", 'OPTIONS'])
@crossdomain(app=app, origin='*')
@basic_auth
def testpost():
    print get_current_logged_in_user()
    return jsonify(request=str(request), request_data=str(request.data))


@app.route('/<username>/ssh_keys/', methods=['GET', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def list_ssh_keys(username):
    """ covered by test 1_users / `Can list user's SSH keys` """
    gw = GitoliteWrapper(GITOLITE_ADMIN_PATH)
    if not gw.user_exists(username):
        return jsonify({"error": "username not found!", "exception": None}), 404
    return jsonify(keys=gw.get_list_of_pretty_key_strings(username))


@app.route('/login/', methods=['POST', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def login():
    json_data = get_json_data()
    username = json_data.get("username")
    password = json_data.get("password")
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    result = dbw.login(username, password)
    if not result:
        return jsonify({"error": "bad login credentials!", "exception": None}), 400
    return jsonify({"token": result}), 200


@app.route('/<username>/ssh_keys/', methods=['POST', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def post_new_ssh_key(username):
    """ covered by 1_users / `User can add an ssh key` """
    json_data = get_json_data()
    if False:  # TODO: ensure that username exists
        return jsonify({"error": "username does not exist"}), 404

    pkey_contents = json_data.get("pkey_contents")

    if not pkey_contents:
        return jsonify({"error": "No key was given!"}), 400

    gw = GitoliteWrapper(GITOLITE_ADMIN_PATH)

    try:
        pretty_key_hex = gw.add_pkey_to_user(username, pkey_contents)
        return jsonify(key_added=pretty_key_hex)
    except InvalidKeyException as e:
        return jsonify({"error": "Public key was invalid format", "exception": str(e)}), 400
    except KeyAlreadyExistsError as e:
        return jsonify({"error": "Public key already exists", "exception": str(e)}), 400
    except UserDoesNotExistError as e:
        return jsonify({"error": "username not found!", "exception": str(e)}), 404


@app.route('/<username>/ssh_keys/', methods=['DELETE', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def remove_key_from_user(username):
    """ covered by 1_users / `User can delete an existing key from themselves` """
    json_data = get_json_data()
    pkey = json_data.get("pkey")

    gw = GitoliteWrapper(GITOLITE_ADMIN_PATH)

    try:
        result = gw.remove_key_from_user_by_pretty_string(username, pkey)
    except KeyDoesNotExistError as e:
        return jsonify({"error": "Key does not exist for user!", "exception": str(e)}), 404
    except CannotDeleteOnlyKeyError as e:
        return jsonify({"error": "Can't delete the only key on the account!", "exception": str(e)}), 400
    if not result:
        return jsonify({"error": "Key was not found under user!", "exception": None}), 404
    return list_ssh_keys(username)


@app.route('/<username>/update/', methods=['POST', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def update_user_info():
    json_data = get_json_data()
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    username = get_current_logged_in_user()
    if username is None:
        username = "konrad"  # TODO: instead raise here
    new_email = json_data.get("email")
    dbw.update_email(username, new_email)
    return jsonify(email_added=new_email)


@app.route('/signup/', methods=['POST', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def signup():
    json_data = get_json_data()
    username = json_data.get("username")
    password = json_data.get("password")
    email = json_data.get("email")
    if '@' not in parseaddr(email)[1]:
        return jsonify({"error": "Invalid email address: "+str(email)})
    if len(password) < 8:
        return jsonify({"error": "Invalid password; must be 8 characters or more"})
    first_name = json_data.get("firstname")
    last_name = json_data.get("lastname")

    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        dbw.create_user(username, email, password, first_name, last_name)
    except UsernameAlreadyTakenError as e:
        return jsonify({"error": "Username is already taken!", "exception": str(e)}), 400
    except EmailAlreadyTakenError as e:
        return jsonify({"error": "Email is already taken!", "exception": str(e)}), 400
    result = dbw.login(username, password)
    return jsonify({"token": result}), 200


@app.route('/<username>/update_password/<temp_password_key>/', methods=['POST', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def update_user_password():
    json_data = get_json_data()
    dbw = DatabaseWrapper()
    username = "konrad"
    new_password = json_data.get("password")
    dbw.update_password(username, new_password)
    return jsonify(password_added=new_password)


@app.route('/classes/', methods=['GET', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def list_classes():
    """ covered by test 0_classes / `Can list classses` """
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    return jsonify(classes=dbw.get_all_classes())


@app.route('/classes/', methods=["POST", 'OPTIONS'])
@crossdomain(app=app, origin='*')
def new_class():
    """ covered by test 0_classes / `Can create classes` """
    json_data = get_json_data()
    class_name = json_data.get("class_name")
    url_name = json_data.get("url_name")
    description = json_data.get("description")

    owner = get_current_logged_in_user()
    if owner is None:
        owner = "spencer"  # TODO: instead raise here
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        c = dbw.create_class(url_name, class_name, description, owner)
        return jsonify(class_created=url_name)
    except UrlNameAlreadyTakenError as e:
        return jsonify({"error": "Url name was already taken!", "exception": str(e)}), 403


@app.route('/classes/<class_url>/', methods=['GET', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def get_class(class_url):
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    return jsonify({"class": dbw.get_class_or_error(class_url)})


@app.route('/classes/<class_url>/projects/', methods=['GET', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def list_projects(class_url):
    """ covered by test 2_projects / `Can list projects in a class` """
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    return jsonify(projects=dbw.get_all_projects_for_class(class_url))


@app.route('/classes/<class_url>/owner/', methods=['GET', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def class_owner(class_url):
    """ covered by test 0_classes / `Can get the owner of a class`"""
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        class_obj = dbw.get_class_or_error(class_url)
        return jsonify(owner=class_obj["owner"])
    except ClassDoesNotExistError as e:
        return jsonify({"error": "class not found!", "exception": str(e)}), 404


@app.route('/classes/<class_url>/teachers/', methods=['GET', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def class_teachers(class_url):
    """ covered by test 0_classes / `Can get the teachers of a class`"""
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        class_obj = dbw.get_class_or_error(class_url)
        return jsonify(teachers=class_obj["teachers"])
    except ClassDoesNotExistError as e:
        return jsonify({"error": "class not found!", "exception": str(e)}), 404


@app.route('/classes/<class_url>/students/', methods=['GET', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def class_students(class_url):
    """ civered by test 0_classes / `Can list students in a class` """
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        class_obj = dbw.get_class_or_error(class_url)
        return jsonify(students=class_obj["students"])
    except ClassDoesNotExistError as e:
        return jsonify({"error": "class not found!", "exception": str(e)}), 404


@app.route('/classes/<class_url>/student/', methods=["POST", 'OPTIONS'])
@crossdomain(app=app, origin='*')
def add_student(class_url):
    """ covered by test 0_classes / `Student can enroll in a class` """
    json_data = get_json_data()
    student = json_data.get("username")
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)

    try:
        dbw.add_student_to_class(class_url, student)
    except ClassDoesNotExistError as e:
        return jsonify({"error": "class not found!", "exception": str(e)}), 404
    except UserDoesNotExistError as e:
        return jsonify({"error": "username not found!", "exception": str(e)}), 404

    return jsonify(class_updated=dbw.get_class_or_error(class_url))


@app.route('/classes/<class_url>/teacher/', methods=["POST", 'OPTIONS'])
@crossdomain(app=app, origin='*')
def add_teacher(class_url):
    """ covered by test 0_classes / `Teacher can add other teachers to class they own` """
    json_data = get_json_data()
    teacher = json_data.get("username")
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)

    try:
        dbw.add_teacher_to_class(class_url, teacher)
    except ClassDoesNotExistError as e:
        return jsonify({"error": "class not found!", "exception": str(e)}), 404
    except UserDoesNotExistError as e:
        return jsonify({"error": "username not found!", "exception": str(e)}), 404

    return jsonify(class_updated=dbw.get_class_or_error(class_url))


@app.route('/classes/<class_url>/projects/<project_url>/', methods=['GET', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def get_project(class_url, project_url):
    """ covered by test 2_projects / `Can list projects in a class` """
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    return jsonify(project=dbw.get_project_or_error(class_url, project_url))


@app.route('/classes/<class_url>/projects/<project_url>/owner/', methods=['GET', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def get_project_owner(class_url, project_url):
    """ covered by test 2_projects / `Can get owner of a project` """
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        project_obj = dbw.get_project_or_error(class_url, project_url)
        return jsonify(owner=project_obj["owner"])
    except ClassDoesNotExistError as e:
        return jsonify({"error": "project not found!", "exception": str(e)}), 404


@app.route('/classes/<class_url>/projects/', methods=["POST", 'OPTIONS'])
@crossdomain(app=app, origin='*')
def new_project(class_url):
    """ covered by test 2_projects / `Teacher can create new project` """
    json_data = get_json_data()
    project_name = json_data.get("project_name")
    url_name = json_data.get("url_name")
    description = json_data.get("description")
    team_based = json_data.get("team_based") in ["True", "true", "Yes", "yes"]
    max_size = int(json_data.get("max_members"))
    due_date = json_data.get("due_date")  # TODO: check formatting from js

    owner = get_current_logged_in_user()
    if owner is None:
        owner = "spencer"  # TODO: instead raise here

    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        dbw.create_project(url_name, project_name, description, class_url, team_based, due_date, owner, max_size)
        return jsonify(project_created=url_name)
    except UrlNameAlreadyTakenError as e:
        return jsonify({"error": "Url name was already taken!", "exception": str(e)}), 403
    except ClassDoesNotExistError as e:
        return jsonify({"error": "Class does not exist!", "exception": str(e)}), 404


@app.route('/classes/<class_url>/projects/<project_url>/due_date/', methods=["POST", 'OPTIONS'])
@crossdomain(app=app, origin='*')
def new_project_due_date(class_url, project_url):
    """ covered by test 2_projects / `Can update due date in a project` """
    json_data = get_json_data()
    due_date = json_data.get("date")
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    return jsonify(project_updated=dbw.update_project_due_date(class_url, project_url, due_date))


@app.route('/classes/<class_name>/projects/<project_name>/make_submission/', methods=["POST", 'OPTIONS'])
@crossdomain(app=app, origin='*')
def make_submission(class_name, project_name):
    json_data = get_json_data()
    owner = json_data.get("owner")
    url_name = project_name
    parent_url = class_name + '/' + project_name
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        dbw.create_submission(url_name, project_name, parent_url, owner)
        return jsonify(submission_made=url_name)
    except UrlNameAlreadyTakenError as e:
        return jsonify({"error": "Url name was already taken!", "exception": str(e)}), 403
    except ProjectDoesNotExistError as e:
        return jsonify({"error": "That project does not exist!", "exception": str(e)}), 404
    except ClassDoesNotExistError as e:
        return jsonify({"error": "Class does not exist!", "exception": str(e)}), 404


@app.route('/<username>/submissions/<submission_name>/', methods=['GET', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def get_submission(username, submission_name):
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    gitolite_url = username + "/submissions/" + submission_name
    try:
        submission=dbw.get_submission_or_error(gitolite_url=gitolite_url)
        return jsonify(submission=submission)
    except SubmissionDoesNotExistError as e:
        return jsonify(error="submission does not exist!", exception=str(e)), 404


@app.route('/<username>/submissions/<submission_name>/', methods=["DELETE", 'OPTIONS'])
@crossdomain(app=app, origin='*')
def delete_user_submission(username, submission_name):
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    gitolite_url = username + "/submissions/" + submission_name
    try:
        dbw.delete_submission(gitolite_url)
        return jsonify(deleted=True)
    except SubmissionDoesNotExistError:
        return jsonify(error="submission does not exist!"), 404


@app.route('/<username>/submissions/<submission_name>/contributors/', methods=['POST', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def add_contributor(username, submission_name):
    json_data = get_json_data()
    new_contributor = json_data.get("username")
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        dbw.add_contributor(username, submission_name, new_contributor)
        return jsonify(contributor_added=new_contributor)
    except StandardError as e:
        return jsonify({"error": "Placeholder error until exceptions are raised by the backend.", "exception": str(e)}), 404


@app.route('/<username>/submissions/<submission_name>/contributors/<removed_username>/', methods=['DELETE', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def remove_contributor(username, submission_name, removed_username):
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        dbw.remove_contributor(username, submission_name, removed_username)
        return jsonify(contributor_removed=removed_username)
    except StandardError as e:
        return jsonify({"error": "Placeholder error until exceptions are raised by the backend.", "exception": str(e)}), 404


@app.route('/<username>/submissions/<submission_name>/contributors/', methods=['GET', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def get_contributors(username, submission_name):
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    return dbw.get_contributors(username, submission_name)


# Note: this is not a routed method
def get_file_or_directory(local_path, commit_path, filepath):
    repo = GitRepo(local_path)
    object = repo.get_file_or_directory(commit_path, filepath)

    resp = Response(mimetype="text/plain")

    if object["type"] == "tree":
        resp.headers['is_tree'] = True
        response_content = ""
        for item in object["file_list"]:
            response_content += item["name"]
            if item["type"] == "tree":
                response_content += "/"
            response_content += "\n"
        resp.set_data(response_content)
    else:
        resp.set_data(object["content"])
    return resp


@app.route('/<username>/submissions/<submission_name>/source/<commit_path>/<path:filepath>', methods=['GET', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def get_submission_file_or_directory(username, submission_name, commit_path, filepath):
    git_repo_path = username + "/submissions/" + submission_name
    local_path = STATIC_REPOS_ROOT + "/" + git_repo_path + ".git"
    return get_file_or_directory(local_path, commit_path, filepath)


@app.route('/classes/<class_url>/projects/<project_url>/source/<commit_path>/<path:filepath>', methods=['GET', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def get_project_file_or_directory(class_url, project_url, commit_path, filepath):
    git_repo_path = class_url + "/" + project_url
    local_path = STATIC_REPOS_ROOT + "/" + git_repo_path + ".git"
    return get_file_or_directory(local_path, commit_path, filepath)


@app.route('/<username>/projects/', methods=['GET', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def get_projects_for_user(username):
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    return jsonify({"projects": dbw.get_projects_for_user(username)})


@app.route('/<username>/submissions/', methods=['GET', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def get_submissions_for_user(username):
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    return jsonify({"submissions": dbw.get_submissions_for_user(username)})


@app.route('/<username>/classes/', methods=['GET', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def get_classes_for_user(username):
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    return jsonify({"classes": dbw.get_classes_for_user(username)})


@app.route('/<username>/landing/', methods=['GET', 'OPTIONS'])
@crossdomain(app=app, origin='*')
def get_landing_for_user(username):
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    classes = dbw.get_classes_for_user(username)
    projects = dbw.get_projects_for_user(username)
    submissions = dbw.get_submissions_for_user(username)
    return jsonify(dict(classes=classes, projects=projects, submissions=submissions))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5556)
