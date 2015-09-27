*** Settings ***
Documentation     A test suite with tests pertaining to the ssh key portion of the API
Resource          ../../resources/resource.robot
Library           ../../libraries/SSHKeyLib.py
Library           ../../libraries/HTTPClientLib.py
Library           Collections

*** Test Cases ***
Can list SSH keys of existing user
    HTTP Status Of Get URL Should Be    ${SERVER}/${TEST_USERNAME}/ssh_keys/    200

Can add an SSH key to an existing user
    # TODO: auth here
    ${$initial_keylist_length}=   get number of keys associated with user  ${TEST_USERNAME}
    ${key_dict}=    create bogus key
    ${pkey_contents}=    get from dictionary    ${key_dict}    pubkey_contents
    ${payload}=    create dictionary    pkey_contents    ${pkey_contents}
    HTTP Status Of Post URL Should Be    ${SERVER}/${TEST_USERNAME}/ssh_keys/    ${payload}    200
    ${keylist_length_after_insert}=    get number of keys associated with user  ${TEST_USERNAME}
    should be equal as integers    ${keylist_length_after_insert}    ${$initial_keylist_length} + 1


Cannot add an SSH key to user if it already exists
    # TODO: auth here
    ${$initial_keylist_length}=   get number of keys associated with user  ${TEST_USERNAME}
    ${key_dict}=    create bogus key
    ${pkey_contents}=    get from dictionary    pubkey_contents
    ${payload}=    create dictionary    pkey_contents    ${pkey_contents}
    # First time should be fine
    HTTP Status Of Post URL Should Be    ${SERVER}/${TEST_USERNAME}/ssh_keys/    ${payload}    200
    # Second time should get an error
    HTTP Status Of Post URL Should Be    ${SERVER}/${TEST_USERNAME}/ssh_keys/    ${payload}    400
    ${keylist_length_after_insert}=    get number of keys associated with user  ${TEST_USERNAME}
    should be equal as integers    ${keylist_length_after_insert}    ${$initial_keylist_length} + 1

Cannot add an invalid SSH key to user
    ${$initial_keylist_length}=   get number of keys associated with user  ${TEST_USERNAME}
    ${payload}=    create dictionary    pkey_contents    this is not a valid public key ya nerd
    HTTP Status Of Post URL Should Be    ${SERVER}/${TEST_USERNAME}/ssh_keys/    ${payload}    400
    ${keylist_length_after_insert}=    get number of keys associated with user  ${TEST_USERNAME}
    should be equal as integers    ${keylist_length_after_insert}    ${$initial_keylist_length}


*** Keywords ***
Get number of keys associated with user
    [Arguments]    ${username}
    ${request}=    get url    ${SERVER}/${username}/ssh_keys/
    ${request_json}=    get http json content from request    ${request}
    dictionary should contain key    ${request_json}    keys
    ${keylist}=    get from dictionary    ${request_json}    keys
    ${keylist_length}=    get length    ${keylist}
    [Return]    ${keylist_length}