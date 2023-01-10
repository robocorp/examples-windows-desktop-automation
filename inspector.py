from ExtendedWindows import ExtendedWindows
import flet as ft
import threading
import pythoncom
import queue
import uiautomation as auto

from pynput_robocorp import mouse
import ctypes

PROCESS_PER_MONITOR_DPI_AWARE = 2

ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)

default_code_text = """*** Settings ***
Library   RPA.Windows

*** Tasks ***
Example Task
    Control Window   ${WINDOW}
    ${element}=   Get Element   ${LOCATOR}
    Click   ${element}
"""
md1 = """
    
# 

[Docs](https://robocorp.com/docs/libraries/rpa-framework)  [Portal](https://portal.robocorp.com)
    
"""


class MyException(Exception):
    pass


def windows_action(queue):  # , locator):
    pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)

    print("INSPECT", flush=True)
    results = []
    # print(f"LOCATOR = {locator}", flush=True)
    # result = []
    # if len(locator.strip()) > 0:
    #     try:
    #         result = ExtendedWindows().print_tree(locator)
    #     except Exception as err:
    #         print(str(err), flush=True)
    #     finally:
    #         print("INSPECT DONE", flush=True)
    def on_click(x, y, button, pressed):
        # control = auto.ControlFromPoint(x, y)
        # control = auto.GetFocusedControl()  # After click
        control = auto.ControlFromCursor()  # For moving around
        root = control.GetTopLevelControl()
        results.append(control)
        results.append(root)
        return False

    def on_move(x, y):
        print("Pointer moved to {0}".format((x, y)))

    def win32_event_filter(msg, data):
        # print(msg, data)
        if msg == 512:
            print("Suppressing left mouse")
            listener._suppress = True
            print(data)
            return False  # if you return False, your on_press/on_release will not be called
        else:
            listener._suppress = False
        return True

    # print("SHOULD RETURN", flush=True)
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    # with mouse.Events() as events:
    #     for event in events:
    #         if hasattr(event, "button") and event.button == mouse.Button.left:
    #             # control = auto.ControlFromCursor()
    #             # control = auto.GetFocusedControl()
    #             control = auto.ControlFromPoint(event.x, event.y)
    #             root = control.GetTopLevelControl()
    #             results.append(control)
    #             results.append(root)
    #             break

    queue.put(results)


def flet_main(page: ft.Page):
    page.scroll = "auto"
    page.title = "Windows Inspector by Mika"
    page.window_width = 600  # window's width is 200 px
    page.window_height = 650  # window's height is 200 px
    title = ft.Text(value="Windows Inspector", color="black")

    page.add(
        ft.Markdown(
            md1,
            selectable=True,
            extension_set="gitHubWeb",
            code_theme="atom-one-dark",
            code_style=ft.TextStyle(font_family="Roboto Mono"),
            on_tap_link=lambda e: page.launch_url(e.data),
        )
    )
    element_textfield = ft.TextField(
        label="Element information", read_only=True, min_lines=6, max_lines=6
    )
    code_text = ft.Text(
        max_lines=9,
        no_wrap=True,
        selectable=True,
        value=default_code_text,
        visible=False,
    )

    page.controls.append(title)
    page.update()

    def btn_click(e):
        # if not txt_name.value:
        #     txt_name.error_text = "Please give locator"
        #     page.update()
        # else:
        #     locator = txt_name.value
        #     page.clean()
        #     inspect_result = WIN.print_tree(locator)
        #     page.add(ft.Text(inspect_result))
        q = queue.Queue()
        thread = threading.Thread(target=windows_action, args=(q,))
        thread.start()
        control, root = q.get()
        # print(f"RESULT: {result}", flush=True)
        # for r in result:
        update_field_information(control, root, element_textfield, code_text, page)

    def btn_copy_code(e):
        page.set_clipboard(code_text.value)

    def btn_showhide_code(e):
        code_text.visible = True
        page.update()

    button_row = ft.Row(
        spacing=0,
        controls=[
            ft.ElevatedButton("Inspect", on_click=btn_click),
            ft.ElevatedButton("Copy Code", on_click=btn_copy_code),
            ft.ElevatedButton("Show Code", on_click=btn_showhide_code),
        ],
    )
    page.add(element_textfield, code_text, button_row)


def update_field_information(control, root, element_textfield, code_text, page):
    print(f"\tCONTROL: {dir(control)}", flush=True)
    print(f"\t{control.AutomationId}", flush=True)
    print(f"\t{control.BoundingRectangle}", flush=True)
    print(f"\t{control.ClassName}", flush=True)
    print(f"\t{control.ControlTypeName}", flush=True)
    print(f"\t{control.foundIndex}", flush=True)
    print(f"\t{control.GetWindowText()}", flush=True)
    # if hasattr(control, "ValuePattern"):
    #     print(f"\tValue: {control.ValuePattern.Value}", flush=True)

    # print(f"\n\tROOT: {dir(root)}", flush=True)

    # if hasattr(root, "ValuePattern"):
    #     print(f"\tValue: {root.ValuePattern.Value}", flush=True)
    element_textfield.value = f"CONTROL: {control.Name}\nROOT: {root.Name}"
    new_text = (
        default_code_text.replace("${WINDOW}", f'name:"{root.Name}"')
        .replace("${LOCATOR}", f'name:"{control.Name}"')
        .replace("\\", "\\\\")
    )

    # TODO. Checkbox selection attributes to use for the matching

    code_text.value = new_text
    page.update()


def main():
    ft.app(target=flet_main)


if __name__ == "__main__":
    main()
