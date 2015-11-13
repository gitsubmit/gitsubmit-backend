*** Settings ***
Documentation     Test suite that contains tests related to git actions
Resource          resource.robot
Library           LocalActionsLib


*** Test Cases ***
Can list classses
    [Tags]  api  database  classes
    Given testing webserver is running
    Then should be able to clone a test repo

*** Keywords ***
should be able to clone a test repo
    clone known project  ${TEMP_PATH}
    known project should exist  ${TEMP_PATH}
