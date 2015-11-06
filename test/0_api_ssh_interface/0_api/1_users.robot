*** Settings ***
Documentation     Test suite that contains tests related to the API / Users
Resource          resource.robot
Library           APIClientLib
Library           HTTPClientLib
Library           Collections


*** Test Cases ***
Can list user's SSH keys
    [Tags]  api  database  users  sshkeys
    Given testing webserver is running
    And user student1 is logged in
    Then there should be 1 keys when user asks for a list of student1's keys

User can add an ssh key
    [Tags]  api  database  users  sshkeys
    Given testing webserver is running
    And user student1 is logged in
    When student1 adds a randomized key to their account
    Then there should be 2 keys when user asks for a list of student1's keys
    And there should be 1 keys when user asks for a list of student2's keys

User cannot add the same key twice
    [Tags]  api  database  users  sshkeys
    Given testing webserver is running
    And user student1 is logged in
    When student1 attempts to add preset key 1 to their account successfully
    Then there should be 3 keys when user asks for a list of student1's keys

    And When student1 attempts to add preset key 1 to their account unsuccessfully
    Then there should be 3 keys when user asks for a list of student1's keys

User cannot add a key if another user already has that key
    [Tags]  api  database  users  sshkeys
    Given testing webserver is running
    And user student1 is logged in
    When student1 attempts to add preset key 2 to their account successfully
    Then there should be 4 keys when user asks for a list of student1's keys

    Then When user student2 is logged in
    And student2 attempts to add preset key 2 to their account unsuccessfully
    Then there should be 1 keys when user asks for a list of student2's keys

User can delete an existing key from themselves
    [Tags]  api  database  users  sshkeys
    Given testing webserver is running
    And user student1 is logged in
    When User removes first key of student1 successfully
    Then there should be 3 keys when user asks for a list of student1's keys

User cannot delete their last key
    [Tags]  api  database  users  sshkeys
    Given testing webserver is running
    And user student2 is logged in
    When User removes first key of student2 unsuccessfully
    Then there should be 1 keys when user asks for a list of student2's keys

User cannot delete other users keys
    [Tags]  api  database  users  sshkeys  not_implemented
    Given testing webserver is running
    And user student2 is logged in
    When User removes first key of student1 unsuccessfully
    Then there should be 3 keys when user asks for a list of student1's keys

*** Keywords ***
Get list of keys for ${user}
    ${obj}=  list keys for user  ${ROOT_URL}  ${user}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
    ${obj}=  get list of keys for ${user}
    ${content}=  get from dictionary  ${obj}  data
    ${keys}=  get from dictionary  ${content}  keys
    [Return]  ${keys}

Get number of keys for ${user}
    ${keys}=  get list of keys for ${user}
    ${len_keys}=  get length  ${keys}
    [Return]  ${len_keys}

Get contents of first key for ${user}
    ${keys}=  get list of keys for ${user}
    ${content}=  get from list  ${keys}  0
    [Return]  ${content}

User removes first key of ${user} successfully
    ${key}=  get contents of first key for ${user}
    ${obj}=  remove key from user  ${ROOT_URL}  ${user}  ${key}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200

User removes first key of ${user} unsuccessfully
    ${key}=  get contents of first key for ${user}
    ${obj}=  remove key from user  ${ROOT_URL}  ${user}  ${key}
    ${code}=  get from dictionary  ${obj}  status_code
    should not be equal as integers  ${code}  200

There should be ${number_keys} keys when user asks for a list of ${user}'s keys
    ${len_keys}=  Get number of keys for ${user}
    # We pre-inserted two classes, so they should be there
    should be equal as integers  ${len_keys}  ${number_keys}

${user} adds a randomized key to their account
    ${obj}=  add randomized key to user  ${ROOT_URL}  ${user}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200


${user} attempts to add preset key 1 to their account successfully
    ${obj}=  add preset key1 to user  ${ROOT_URL}  ${user}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200


${user} attempts to add preset key 1 to their account unsuccessfully
    ${obj}=  add preset key1 to user  ${ROOT_URL}  ${user}
    ${code}=  get from dictionary  ${obj}  status_code
    should not be equal as integers  ${code}  200


${user} attempts to add preset key 2 to their account successfully
    ${obj}=  add preset key2 to user  ${ROOT_URL}  ${user}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200


${user} attempts to add preset key 2 to their account unsuccessfully
    ${obj}=  add preset key2 to user  ${ROOT_URL}  ${user}
    ${code}=  get from dictionary  ${obj}  status_code
    should not be equal as integers  ${code}  200


