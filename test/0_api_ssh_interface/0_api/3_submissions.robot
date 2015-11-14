*** Settings ***
Documentation     Test suite that contains tests related to the API / Classes
Resource          resource.robot
Library           APIClientLib
Library           HTTPClientLib
Library           Collections

*** Test Cases ***
Can get submission individually
    [Tags]  api  database  submissions
    Given testing webserver is running
    And user teacher1 is logged in
    Then Get user "student1"'s submission titled "turned_on_a_computer" individually

*** Keywords ***
Get user "${user}"'s submission titled "${submission}" individually
    ${obj}=  get submission individually  ${ROOT_URL}  ${user}  ${submission}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
    ${content}=  get from dictionary  ${obj}  data
    [Return]  ${content}
