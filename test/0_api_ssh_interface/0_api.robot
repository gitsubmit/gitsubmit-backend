*** Settings ***
Documentation     Test suite that contains tests related to the API
Resource          ../resources/resource.robot


*** Test Cases ***
Can create class
    [Tags]  database  class
    Given testing webserver is running
    And teacher user is logged in
