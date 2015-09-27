*** Settings ***
Documentation     A test suite with tests pertaining to the ssh key portion of the API
Resource          ../../resources/resource.robot
Library           ../../libraries/SSHKeyLib.py
Library           ../../libraries/HTTPClientLib.py
Library           Collections

*** Test Cases ***
Can list SSH keys of existing user
    HTTP Status Of Get URL Should Be    ${ROOT_URL}/${TEST_USERNAME}/ssh_keys/    200

Can add and delete an SSH key from an existing user
    # TODO: auth here
    ${initial_keylist_length}=   get number of keys associated with user  ${TEST_USERNAME}
    ${key_dict}=    create bogus key
    ${pkey_contents}=    get from dictionary    ${key_dict}    pubkey_contents
    ${payload}=    create dictionary    pkey_contents    ${pkey_contents}
    HTTP Status Of Post URL Should Be    ${ROOT_URL}/${TEST_USERNAME}/ssh_keys/    ${payload}    200
    ${keylist_length_after_insert}=    get number of keys associated with user  ${TEST_USERNAME}
    ${expected_length}=    evaluate    ${initial_keylist_length} + 1
    should be equal as integers    ${keylist_length_after_insert}    ${expected_length}
    # now delete the key
    ${key_string}=    convert ssh key to colon string    ${pkey_contents}
    ${delete_payload}=    create dictionary    pkey    ${key_string}
    HTTP Status Of Delete URL Should Be    ${ROOT_URL}/${TEST_USERNAME}/ssh_keys/    ${delete_payload}    200
    ${keylist_length_after_delete}=    get number of keys associated with user  ${TEST_USERNAME}
    should be equal as integers    ${keylist_length_after_delete}    ${initial_keylist_length}


Cannot add an SSH key to user if it already exists
    # TODO: auth here
    ${initial_keylist_length}=   get number of keys associated with user  ${TEST_USERNAME}
    ${key_dict}=    create bogus key
    ${pkey_contents}=    get from dictionary    ${key_dict}    pubkey_contents
    ${payload}=    create dictionary    pkey_contents    ${pkey_contents}
    # First time should be fine
    HTTP Status Of Post URL Should Be    ${ROOT_URL}/${TEST_USERNAME}/ssh_keys/    ${payload}    200
    # Second time should get an error
    HTTP Status Of Post URL Should Be    ${ROOT_URL}/${TEST_USERNAME}/ssh_keys/    ${payload}    400
    ${keylist_length_after_insert}=    get number of keys associated with user  ${TEST_USERNAME}
    ${expected_length}=    evaluate    ${initial_keylist_length} + 1
    should be equal as integers    ${keylist_length_after_insert}    ${expected_length}

Cannot add an invalid SSH key to user
    ${initial_keylist_length}=   get number of keys associated with user  ${TEST_USERNAME}
    ${payload}=    create dictionary    pkey_contents    this is not a valid public key ya nerd
    HTTP Status Of Post URL Should Be    ${ROOT_URL}/${TEST_USERNAME}/ssh_keys/    ${payload}    400
    ${keylist_length_after_insert}=    get number of keys associated with user  ${TEST_USERNAME}
    should be equal as integers    ${keylist_length_after_insert}    ${initial_keylist_length}

Cannot delete last key from user
    delete all but one key from user    ${TEST_USERNAME}
    ${keylist}=    get list of keys associated with user
    ${last_key}=    get from list    ${keylist}    0
    ${delete_payload}=    create dictionary    pkey    ${last_key}
    HTTP Status Of Delete URL Should Be    ${ROOT_URL}/${TEST_USERNAME}/ssh_keys/    ${delete_payload}    400


*** Keywords ***
Get list of keys associated with user
    [Arguments]    ${username}
    ${request}=    get url    ${ROOT_URL}/${username}/ssh_keys/
    ${request_json}=    get http json content from request    ${request}
    dictionary should contain key    ${request_json}    keys
    @{keylist}=    get from dictionary    ${request_json}    keys
    [Return]    @{keylist}

Get number of keys associated with user
    [Arguments]    ${username}
    ${keylist}=    get list of keys associated with user  ${username}
    ${keylist_length}=    get length    ${keylist}
    [Return]    ${keylist_length}

Delete all but one key from user
    [Arguments]    ${username}
    ${number_of_keys}=   get number of keys associated with user    ${username}
    @{list}=    get list of keys associated with user    ${username}
    :FOR    ${index}    IN RANGE    1    ${number_of_keys}
    \    ${delete_payload}=    create dictionary    pkey    @{list}[${index}]
    \    HTTP Status Of Delete URL Should Be    ${ROOT_URL}/${username}/ssh_keys/    ${delete_payload}    200

