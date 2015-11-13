*** Settings ***
Documentation     Test suite that contains tests related to the Git File API / Classes
Resource          resource.robot
Suite Setup       get filesystem from docker instance

*** Test Cases ***
Do soemthing
    get filesystem from docker instance

*** Keywords ***
Get filesystem from docker instance
    log  ok neat