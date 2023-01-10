*** Settings ***
Library     RPA.Windows


*** Tasks ***
Example Task
    Control Window    name:"Calculator"
    ${element}=    Get Element    name:"Eight"
    Click    ${element}
