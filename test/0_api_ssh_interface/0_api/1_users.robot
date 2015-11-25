*** Settings ***
Documentation     Test suite that contains tests related to the API / Users
Resource          resource.robot
Library           APIClientLib
Library           HTTPClientLib
Library           Collections


*** Test Cases ***
User can log in
    [Tags]  api  database  users  login
    Given testing webserver is running
    Then should get a token when logging in

User can signup
    [Tags]  api  database  users  signup
    Given testing webserver is running
    Then should get a token when signing up

Can list user's SSH keys
    [Tags]  api  database  users  sshkeys
    Given testing webserver is running
    And user student1 is logged in
    # this will fail if we can't list keys
    Then get list of keys for student1

User can add an ssh key
    [Tags]  api  database  users  sshkeys
    Given testing webserver is running
    And user student1 is logged in
    Then keys for student1 should go up by one after adding a randomized ssh key

User cannot add the same key twice
    [Tags]  api  database  users  sshkeys
    Given testing webserver is running
    And user student1 is logged in
    Then Keys for student1 should only go up by one if the same key is added twice

User cannot add a key if another user already has that key
    [Tags]  api  database  users  sshkeys  not_implemented
    Given testing webserver is running
    And user student1 is logged in
    Then Keys for student1 should not change if they attempt to add a key student2 else already has

User can delete an existing key from themselves
    [Tags]  api  database  users  sshkeys
    Given testing webserver is running
    And user student1 is logged in
    Then "student1" can add then remove a key

User cannot delete their last key
    [Tags]  api  database  users  sshkeys
    Given testing webserver is running
    And user student2 is logged in
    When user removes all but one key  ${ROOT_URL}  student2
    Then there should be 1 keys when user asks for a list of student2's keys
    And cannot remove key from student2

User cannot delete other users keys
    [Tags]  api  database  users  sshkeys  not_implemented
    Given testing webserver is running
    And user student2 is logged in
    Then Cannot remove key from student1

User has a landing page
    [Tags]  api  database  users
    Given testing webserver is running
    And user student2 is logged in
    Then Can get landing page for user "student2"

Invalid email: empty
    [Tags]  api  database  users  signup  email  invalid
    Given testing webserver is running
    Then should get 400 when signing up as "user" with password "validpassword" and email ""

Invalid email: no '@' in email
    [Tags]  api  database  users  signup  email  invalid
    Given testing webserver is running
    Then should get 400 when signing up as "user" with password "validpassword" and email "bademailatgitsubmit.com"

Invalid password: empty
    [Tags]  api  database  users  signup  password  invalid
    Given testing webserver is running
    Then should get 400 when signing up as "user" with password "" and email "email@gitsubmit.com"

Invalid password: short
    [Tags]  api  database  users  signup  password  invalid
    Given testing webserver is running
    Then should get 400 when signing up as "user" with password "1234567" and email "email@gitsubmit.com"

Invalid user: empty
    [Tags]  api  database  users  signup user  invalid
    Given testing webserver is running
    Then should get 400 when signing up as "" with password "validpassword" and email "email@gitsubmit.com"


*** Keywords ***
should get a token when logging in
    ${obj}=  log known user in  ${ROOT_URL}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
    ${content}=  get from dictionary  ${obj}  data
    dictionary should contain key  ${content}  token

should get a token when logging in
    ${obj}=  signup  known  user  ${ROOT_URL}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
    ${content}=  get from dictionary  ${obj}  data
    dictionary should contain key  ${content}  token

Cannot remove key from ${user}
    ${keys_before}=  get number of keys for ${user}
    User removes first key of ${user} unsuccessfully
    There should be ${keys_before} keys when user asks for a list of ${user}'s keys

"${user}" can add then remove a key
    ${keys_before}=  get number of keys for ${user}
    ${expected_after_add}=  evaluate  ${keys_before} + 1
    "${user}" adds a randomized key to their account
    ${actual_after_add}=  get number of keys for ${user}
    should be equal as integers  ${actual_after_add}  ${expected_after_add}

    User removes first key of ${user} successfully
    there should be ${keys_before} keys when user asks for a list of student1's keys

Keys for ${user} should not change if they attempt to add a key ${other_user} else already has
    ${other_keys_before}=  get number of keys for ${other_user}
    ${other_expected_after}=  evaluate  ${other_keys_before} + 1
    "${other_user}" attempts to add preset key 2 to their account successfully
    there should be ${other_expected_after} keys when user asks for a list of ${other_user}'s keys

    ${keys_before}=  get number of keys for ${other_user}
    user ${user} is logged in
    "${user}" attempts to add preset key 2 to their account unsuccessfully
    there should be ${keys_before} keys when user asks for a list of ${user}'s keys

Keys for ${user} should only go up by one if the same key is added twice
    ${keys_before}=  get number of keys for ${user}
    ${expected_after}=  evaluate  ${keys_before} + 1
    "${user}" attempts to add preset key 1 to their account successfully
    there should be ${expected_after} keys when user asks for a list of ${user}'s keys

    "${user}" attempts to add preset key 1 to their account unsuccessfully
    there should be ${expected_after} keys when user asks for a list of ${user}'s keys

Keys for ${user} should go up by one after adding a randomized ssh key
    ${num_keys_before}=  get number of keys for ${user}
    ${expected_after}=  evaluate  ${num_keys_before} + 1
    "${user}" adds a randomized key to their account
    ${actual_after}=  get number of keys for ${user}
    should be equal as integers  ${actual_after}  ${expected_after}

Get list of keys for ${user}
    ${obj}=  list keys for user  ${ROOT_URL}  ${user}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
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

"${user}" adds a randomized key to their account
    ${obj}=  add randomized key to user  ${ROOT_URL}  ${user}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200


"${user}" attempts to add preset key 1 to their account successfully
    ${obj}=  add preset key1 to user  ${ROOT_URL}  ${user}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200


"${user}" attempts to add preset key 1 to their account unsuccessfully
    ${obj}=  add preset key1 to user  ${ROOT_URL}  ${user}
    ${code}=  get from dictionary  ${obj}  status_code
    should not be equal as integers  ${code}  200


"${user}" attempts to add preset key 2 to their account successfully
    ${obj}=  add preset key2 to user  ${ROOT_URL}  ${user}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200


"${user}" attempts to add preset key 2 to their account unsuccessfully
    ${obj}=  add preset key2 to user  ${ROOT_URL}  ${user}
    ${code}=  get from dictionary  ${obj}  status_code
    should not be equal as integers  ${code}  200

Can get landing page for user "${user}"
    ${obj}=  get users landing page  ${ROOT_URL}  ${user}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200


should get 400 when signing up as "${user}" with password "${password}" and email "${email}"
    ${obj}=  signup  ${ROOT_URL}  ${user}  ${password}  ${email}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  400
