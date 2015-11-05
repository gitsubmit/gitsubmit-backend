*** Settings ***
Documentation     Test suite that contains tests related to the API
Resource          ../resources/resource.robot
Library           APIClientLib
Library           HTTPClientLib
Library           Collections


*** Test Cases ***
Can list classses
    [Tags]  database  class
    Given testing webserver is running
    And teacher user is logged in
    Then there should be 2 classes when user asks for a list of classes

Can create classes
    Given testing webserver is running
    And teacher user is logged in
    When User creates a new class
    Then there should be 3 classes when user asks for a list of classes

*** Keywords ***
There should be ${number_classes} classes when user asks for a list of classes
    ${obj}=  list classes  ${ROOT_URL}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
    ${content}=  get from dictionary  ${obj}  data
    ${classes}=  get from dictionary  ${content}  classes
    ${number_classes}=  get length  ${classes}
    # We pre-inserted two classes, so they should be there
    should be equal as integers  ${number_classes}  ${number_classes}

User creates a new class
    ${obj}=  create randomized class  ${ROOT_URL}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
