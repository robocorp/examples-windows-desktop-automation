from RPA.Windows import Windows
import uiautomation as auto
from uiautomation import PaneControl
import time

WIN = Windows()


def GetFirstChild(control):
    if isinstance(control, auto.TreeItemControl):
        ecpt = control.GetExpandCollapsePattern()
        if ecpt and ecpt.ExpandCollapseState == auto.ExpandCollapseState.Expanded:
            child = None
            tryCount = 0
            # some tree items need some time to finish expanding
            while not child:
                tryCount += 1
                child = control.GetFirstChildControl()
                if child or tryCount > 20:
                    break
                time.sleep(0.05)
            return child
    else:
        return control.GetFirstChildControl()


def GetNextSibling(control):
    return control.GetNextSiblingControl()


def get_window_texts(window_title):
    window = WIN.control_window(f'name:"{window_title}"')
    details = []
    for control, depth in auto.WalkTree(
        window.item,
        getFirstChild=GetFirstChild,
        getNextSibling=GetNextSibling,
        includeTop=True,
        maxDepth=8,
    ):
        detail = None
        control_identifier = ""
        if hasattr(control, "GetScrollItemPattern"):
            sipt = control.GetScrollItemPattern()
            if sipt:
                sipt.ScrollIntoView(waitTime=0.05)
        if len(control.Name) > 0:
            control_identifier = f'name:"{control.Name}"'
        elif len(control.AutomationId) > 0:
            control_identifier = f"id:{control.AutomationId}"
        elif len(control.ControlTypeName) > 0:
            control_identifier = f"type:{control.ControlTypeName}"
        if hasattr(control, "GetValuePattern"):
            value_pattern = control.GetValuePattern()
            value = value_pattern.Value if value_pattern else ""
            detail = value.replace("\t", " " * 4).split("\r")
            if len(detail) == 1:
                detail = detail[0]
        else:
            detail = control.GetWindowText() or ""
        details.append(
            {
                "locator": control_identifier,
                "locator_with_depth": f"{control_identifier} depth:{depth}",
                "type": control.ControlTypeName,
                "text": detail,
                "depth": depth,
            }
        )
    return details


def minimal_task():
    details = get_window_texts("ListViewEx Demo")
    print("\nDetails:")
    WIN.click('name:"DoubleClickActivation"')
    for d in details:
        print(d)
        if "1976" in d["locator"] and d["type"] == "ListItemControl":
            WIN.click(d["locator_with_depth"])
    WIN.click('name:"DoubleClickActivation"')
    print("Done.")


if __name__ == "__main__":
    minimal_task()
