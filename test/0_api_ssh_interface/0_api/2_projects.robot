*** Settings ***
Documentation     Test suite that contains tests related to the API / Classes
Resource          resource.robot
Library           APIClientLib
Library           HTTPClientLib
Library           Collections


*** Test Cases ***
Can list projects in a class
    [Tags]  api  database  projects
    Given testing webserver is running
    And user teacher1 is logged in
    Then get projects of class "intro_to_computers"

Can get owner of a project
    [Tags]  api  database  projects
    Given testing webserver is running
    And user teacher1 is logged in
    Then get owner of project "use_a_computer" in class "adv_computers"

Teacher can create a new project
    [Tags]  api  database  projects
    Given testing webserver is running
    And user teacher1 is logged in
    Then number of projects in "adv_computers" should increase by one after user creates a randomized project

Cannot create projects with same url
    [Tags]  api  database  classes
    Given testing webserver is running
    And user teacher1 is logged in
    Then Number of projects in "adv_computers" should only increase by one when user creates a predefined project twice

Can update due date in a project
    [Tags]  api  database  classes
    Given testing webserver is running
    And user teacher1 is logged in
    Then Can update the due date for project "use_a_computer" in class "adv_computers" to "2016-08-22"


*** Keywords ***
Can update the due date for project "${project}" in class "${class}" to "${date}"
    ${obj}=  update due date  ${ROOT_URL}  ${class}  ${project}  ${date}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200

Number of projects in "${class}" should only increase by one when user creates a predefined project twice
    ${num_projects}=  get number of projects in class "${class}"
    ${expected_after}=  evaluate  ${num_projects} + 1
    User creates a predefined project in class "${class}" successfully
    There should be ${expected_after} projects in class ${class} when user asks for a list of projects

    User creates the same predefined project in class "${class}" unsuccessfully
    There should be ${expected_after} projects in class ${class} when user asks for a list of projects

number of projects in "${class}" should increase by one after user creates a randomized project
    ${num_classes}=  get number of projects in class "${class}"
    ${expected_after}=  evaluate  ${num_classes} + 1
    User creates a new randomized project in class "${class}"
    there should be ${expected_after} projects in class ${class} when user asks for a list of projects

User creates a predefined project in class "${class}" successfully
    ${obj}=  create predefined project  ${ROOT_URL}  ${class}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200

User creates the same predefined project in class "${class}" unsuccessfully
    ${obj}=  create predefined project  ${ROOT_URL}  ${class}
    ${code}=  get from dictionary  ${obj}  status_code
    should not be equal as integers  ${code}  200

There should be ${number_projects} projects in class ${class} when user asks for a list of projects
    ${len_projects}=  get number of projects in class "${class}"
    should be equal as integers  ${number_projects}  ${len_projects}

User creates a new randomized project in class "${class}"
    ${obj}=  create randomized project  ${ROOT_URL}  ${class}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200

Get owner of project "${project}" in class "${class_name}"
    ${obj}=  get project owner  ${ROOT_URL}  ${class_name}  ${project}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
    ${content}=  get from dictionary  ${obj}  data
    ${owner}=  get from dictionary  ${content}  owner
    [Return]  ${owner}

Get number of projects in class "${class}"
    ${projects}=  get projects of class "${class}"
    ${len_projects}=  get length  ${projects}
    [Return]  ${len_projects}

Get projects of class "${class}"
    ${obj}=  get class projects  ${ROOT_URL}  ${class}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
    ${content}=  get from dictionary  ${obj}  data
    ${projects}=  get from dictionary  ${content}  projects
    [Return]  ${projects}