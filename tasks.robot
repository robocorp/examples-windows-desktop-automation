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
