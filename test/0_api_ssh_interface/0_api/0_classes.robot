*** Settings ***
Documentation     Test suite that contains tests related to the API / Classes
Resource          resource.robot
Library           APIClientLib
Library           HTTPClientLib
Library           Collections


*** Test Cases ***
Can list classses
    [Tags]  api  database  classes
    Given testing webserver is running
    And user teacher1 is logged in
    Then get list of classses

Can get class individually
    [Tags]  api  database  classes
    Given testing webserver is running
    And user teacher1 is logged in
    Then get class "adv_computers" individually

Can create classes
    [Tags]  api  database  classes
    Given testing webserver is running
    And user teacher1 is logged in
    Then Number of classes should increase by one when user creates a randomized class

Cannot create classes with same url
    [Tags]  api  database  classes
    Given testing webserver is running
    And user teacher1 is logged in
    Then Number of classes should only increase by one when user creates a predefined class twice

Can list students in a class
    [Tags]  api  database  classes
    Given testing webserver is running
    And user teacher1 is logged in
    Then Get students enrolled in "intro_to_computers"

Student can enroll in a class
    [Tags]  api  database  classes
    Given testing webserver is running
    And user student1 is logged in
    Then User student1 can enroll in class "adv_computers"

Can get the owner of a class
    [Tags]  api  database  classes
    Given testing webserver is running
    And user student1 is logged in
    Then get owner of class "intro_to_computers"

Can get the teachers of a class
    [Tags]  api  database  classes
    Given testing webserver is running
    And user student1 is logged in
    Then get teachers of class "intro_to_computers"

Teacher can add other teachers to class they own
    [Tags]  api  database  classes
    Given testing webserver is running
    And user teacher1 is logged in
    Then can add teacher teacher2 to class "intro_to_computers"

Can get users classes
    [Tags]  api  database  classes
    Given testing webserver is running
    And user teacher1 is logged in
    Then Can get user "student1"'s classes

*** Keywords ***
Can add teacher ${teacher} to class "${class_name}"
    ${obj}=  add teacher to class  ${ROOT_URL}  ${teacher}  ${class_name}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200

Get owner of class "${class_name}"
    ${obj}=  get class owner  ${ROOT_URL}  ${class_name}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
    ${content}=  get from dictionary  ${obj}  data
    ${owner}=  get from dictionary  ${content}  owner
    [Return]  ${owner}

Get teachers of class "${class_name}"
    ${obj}=  get class teachers  ${ROOT_URL}  ${class_name}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
    ${content}=  get from dictionary  ${obj}  data
    ${teachers}=  get from dictionary  ${content}  teachers
    [Return]  ${teachers}

User ${student} can enroll in class "${class_name}"
    ${obj}=  enroll student in class  ${ROOT_URL}  ${student}  ${class_name}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200

Number of classes should only increase by one when user creates a predefined class twice
    ${num_classes}=  get number of classes
    ${expected_after}=  evaluate  ${num_classes} + 1
    User creates a predefined class successfully
    there should be ${expected_after} classes when user asks for a list of classes

    User attempts to create the same predefined class unsuccessfully
    Then there should be ${expected_after} classes when user asks for a list of classes

Number of classes should increase by one when user creates a randomized class
    ${num_classes}=  get number of classes
    ${expected_after}=  evaluate  ${num_classes} + 1
    User creates a new randomized class
    there should be ${expected_after} classes when user asks for a list of classes

Get students enrolled in "${class}"
    ${obj}=  list students in class  ${ROOT_URL}  ${class}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
    ${content}=  get from dictionary  ${obj}  data
    ${students}=  get from dictionary  ${content}  students
    [Return]  ${students}

Get class "${class}" individually
    ${obj}=  get class individually  ${ROOT_URL}  ${class}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
    ${content}=  get from dictionary  ${obj}  data
    [Return]  ${content}

There should be ${number_students} enrolled in "${class}"
    ${students}=  get students enrolled in "${class}"
    ${len_students}=  get length  ${students}
    # We pre-inserted two classes, so they should be there
    should be equal as integers  ${number_students}  ${len_students}

Get list of classses
    ${obj}=  list classes  ${ROOT_URL}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
    ${content}=  get from dictionary  ${obj}  data
    ${classes}=  get from dictionary  ${content}  classes
    [Return]  ${classes}

Get number of classes
    ${classes}=  get list of classses
    ${num_classes}=  get length  ${classes}
    [Return]  ${num_classes}

There should be ${number_classes} classes when user asks for a list of classes
    ${classes}=  get list of classses
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

Can get user "${user}"'s classes
    ${obj}=  get users classes  ${ROOT_URL}  ${user}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200