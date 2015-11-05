*** Settings ***
Documentation     Test suite that contains tests related to the API / Classes
Resource          ../resources/resource.robot
Library           APIClientLib
Library           HTTPClientLib
Library           Collections


*** Test Cases ***
Can list classses
    [Tags]  api  database  classes
    Given testing webserver is running
    And teacher user is logged in
    Then there should be 2 classes when user asks for a list of classes

Can create classes
    [Tags]  api  database  classes
    Given testing webserver is running
    And teacher user is logged in
    When User creates a new randomized class
    Then there should be 3 classes when user asks for a list of classes

Cannot create classes with same url
    [Tags]  api  database  classes
    Given testing webserver is running
    And teacher user is logged in
    When User creates a predefined class successfully
    Then there should be 4 classes when user asks for a list of classes

    And When User attempts to create the same predefined class unsuccessfully
    Then there should be 4 classes when user asks for a list of classes


*** Keywords ***
There should be ${number_classes} classes when user asks for a list of classes
    ${obj}=  list classes  ${ROOT_URL}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
    ${content}=  get from dictionary  ${obj}  data
    ${classes}=  get from dictionary  ${content}  classes
    ${len_classes}=  get length  ${classes}
    # We pre-inserted two classes, so they should be there
    should be equal as integers  ${number_classes}  ${len_classes}

User creates a new randomized class
    ${obj}=  create randomized class  ${ROOT_URL}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200

User creates a predefined class successfully
    ${obj}=  create predefined class  ${ROOT_URL}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200

User attempts to create the same predefined class unsuccessfully
    ${obj}=  create predefined class  ${ROOT_URL}
    ${code}=  get from dictionary  ${obj}  status_code
    should not be equal as integers  ${code}  200