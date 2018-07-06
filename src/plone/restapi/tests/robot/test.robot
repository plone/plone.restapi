*** Settings ***

Library  Selenium2Library  timeout=10  implicit_wait=0.5

Suite Setup  Start browser
Suite Teardown  Close All Browsers

*** Variables ***

${BROWSER} =  firefox

*** Test Cases ***

Plone site
    [Tags]  start
    Go to  ${PLONE_URL}
    Page should contain  Plone site

*** Keywords ***

Start browser
    Open browser  ${PLONE_URL}  browser=${BROWSER}
