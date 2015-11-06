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

*** Keywords ***
Get owner of project "${project}" in class "${class_name}"
    ${obj}=  get project owner  ${ROOT_URL}  ${class_name}  ${project}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
    ${content}=  get from dictionary  ${obj}  data
    ${owner}=  get from dictionary  ${content}  owner
    [Return]  ${owner}

Get projects of class "${class_name}"
    ${obj}=  get class projects  ${ROOT_URL}  ${class_name}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
    ${content}=  get from dictionary  ${obj}  data
    ${projects}=  get from dictionary  ${content}  projects
    [Return]  ${projects}