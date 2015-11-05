*** Settings ***
Documentation     Test suite that contains tests related to the API / Users
Resource          ../resources/resource.robot
Library           APIClientLib
Library           HTTPClientLib
Library           Collections


*** Test Cases ***
Can list user's SSH keys
    [Tags]  api  database  users
    Given testing webserver is running
    And teacher user is logged in
    Then there should be 1 keys when user asks for a list of student1's keys


*** Keywords ***
There should be ${number_keys} keys when user asks for a list of ${user}'s keys
    ${obj}=  list keys for user  ${ROOT_URL}  ${user}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
    ${content}=  get from dictionary  ${obj}  data
    ${keys}=  get from dictionary  ${content}  keys
    ${len_keys}=  get length  ${keys}
    # We pre-inserted two classes, so they should be there
    should be equal as integers  ${len_keys}  ${number_keys}