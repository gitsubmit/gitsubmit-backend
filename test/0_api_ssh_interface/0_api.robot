*** Settings ***
Documentation     Test suite that contains tests related to the API
Resource          ../resources/resource.robot
Library           APIClientLib
Library           HTTPClientLib
Library           Collections


*** Test Cases ***
Can create class
    [Tags]  database  class
    Given testing webserver is running
    And teacher user is logged in
    ${obj}=  list classes
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
