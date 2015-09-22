*** Settings ***
Documentation     A test suite with a single Gherkin style smoke test.
Resource          ../resources/resource.robot
Library           ../libraries/SmokeLib.py
Test Teardown     Close Browser


*** Test Cases ***
Test Webserver Is Alive
    [Tags]  smoke_test
    Given testing webserver is running
    Then HTTP Status Of URL Should Be  ${ROOT_URL}   200

*** Keywords ***
HTTP Status Of URL Should Be
    [Arguments]  ${URL}   ${CODE}
    ${return_code}=     get url http status   ${ROOT_URL}
    should be equal as integers  ${CODE}  ${return_code}

testing webserver is running
    no operation
    # this is a test prereq but
    # lol gherkin