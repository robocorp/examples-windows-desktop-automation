*** Settings ***
Library     ExtendedWindows


*** Tasks ***
Printing Windows Element Tree
    ${elements}=    Print Tree
    ...    name:"C:\\koodi\\testground"
    ...    log_as_warnings=True
    ...    capture_image_folder=${CURDIR}${/}element_images
    ${len}=    Get Length    ${elements}
    Log to Console    contains ${len} elements
    #Control Window    name:"C:\\koodi\\testground"
    #Double Click    type:ListItem and name:"error-handling"

# RunQuery
#    Connect To MongoDB    127.0.0.1    27017
#    ${QueryJSON}=    Set Variable    { $where: 'this.sharedWith == "user1" && this.email == "contact1@private.info"' }
#    ${allResults}=    Retrieve Some MongoDB Records    test    contacts    ${QueryJSON}
#    Log    ${allResults}
