*** Settings ***
Documentation     A resource file with reusable keywords and variables.
...
...               The system specific keywords created here form our own
...               domain specific language. They utilize keywords provided
...               by the imported Selenium2Library.
...
...               Based on example code at: https://bitbucket.org/robotframework/webdemo/src/6a95fc3744c7?at=master
Library           Selenium2Library
Library           HTTPClientLib
Library           APIClientLib

*** Variables ***
${SERVER}         localhost:5555
${BROWSER}        Chrome
${DELAY}          0
${VALID USER}     demo
${VALID PASSWORD}    demopass
${ROOT_URL}         http://${SERVER}/

*** Keywords ***
testing webserver is running
    no operation
    # this is a test prereq but
    # lol gherkin

user ${user} is logged in
    log in  ${ROOT_URL}  ${user}  verybadpw
