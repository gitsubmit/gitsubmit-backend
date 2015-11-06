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
    Then number of projects in "adv_computers" should increase by 1 after teacher1 creates a randomized project

*** Keywords ***
number of projects in "${class}" should increase by 1 after ${user} creates a randomized project
    ${num_classes}=  get number of projects in class "${class}"
    ${expected_after}=  evaluate  ${num_classes} + 1
    User creates a new randomized project
    there should be ${expected_after} projects in class ${class} when user asks for a list of projects

There should be ${number_projects} projects in class ${class} when user asks for a list of projects
    ${len_projects}=  get number of projects in class "${class}"
    should be equal as integers  ${number_projects}  ${len_projects}

User creates a new randomized project
    ${obj}=  create randomized project  ${ROOT_URL}
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