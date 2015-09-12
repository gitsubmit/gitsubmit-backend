*** Settings ***
Documentation     A resource file with reusable keywords and variables.
...
...               The system specific keywords created here form our own
...               domain specific language. They utilize keywords provided
...               by the imported Selenium2Library.
...
...               Based on example code at: https://bitbucket.org/robotframework/webdemo/src/6a95fc3744c7?at=master
Library           Selenium2Library

*** Variables ***
${SERVER}         gitsubmit.com:5123
${BROWSER}        Chrome
${DELAY}          0
${VALID USER}     demo
${VALID PASSWORD}    pass
${LOGIN URL}      http://${SERVER}/login
${DASHBOARD URL}    http://${SERVER}/dash
${ERROR URL}      http://${SERVER}/error

*** Keywords ***
Open Browser To Login Page
    Open Browser    ${LOGIN URL}    ${BROWSER}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    Login Page Should Be Open

Login Page Should Be Open
    Title Should Be    GitSubmit - Login

Go To Login Page
    Go To    ${LOGIN URL}
    Login Page Should Be Open

Input Username
    [Arguments]    ${username}
    Input Text    username_field    ${username}

Input Password
    [Arguments]    ${password}
    Input Text    password_field    ${password}

Submit Credentials
    Click Button    login_button

Welcome Page Should Be Open
    Location Should Be    ${DASHBOARD URL}
    Title Should Be    GitSubmit - Dashboard