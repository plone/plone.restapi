*** Settings ***

Library  Collections
Library  RequestsLibrary

Suite Setup  Suite Setup
Suite Teardown  Suite Teardown

*** Variables ***

${HOST}  http://localhost
${PORT}  55001

*** Test Cases ***

Plone site
  ${response}=  Get Request  plone  /
  Should Be Equal As Strings  ${response.status_code}  200
  Log  ${response}

*** Keywords ***

Suite Setup
  Create Session  plone  ${HOST}:${PORT}/plone/

Suite Teardown
  No operation
