from RPA.Windows import Windows, ElementKeywords, LocatorKeywords
from RPA.Windows.keywords import keyword, LibraryContext
from pathlib import Path
from typing import List, Optional
from RPA.core.windows.locators import Locator
from RPA.Windows import utils
import time

if utils.IS_WINDOWS:
    import uiautomation as auto
    from uiautomation import TreeNode

    auto.SetGlobalSearchTimeout(1.0)


class ExtendedWindows(Windows):
    def _get_libraries(self, locators_path: Optional[str]):
        return [ExtendedElements(self), LocatorKeywords(self)]


class ExtendedElements(ElementKeywords):
    @keyword
    def print_tree(
        self,
        locator: Optional[Locator] = None,
        max_depth: int = 8,
        capture_image_folder: Optional[str] = None,
        log_as_warnings: bool = False,
    ) -> None:
        """Print Control element tree.

        Windows application structure can contain multilevel element
        structure. Understanding this structure is important for
        creating locators.

        This keyword can be used to output application element structure
        starting with the element defined by the `locator`.

        :param locator: string locator or Control element
        :param max_depth: maximum depth level (defaults to 8)
        :param capture_image_folder: if None images are not captured
        :param log_as_warnings: if set log messages are visible on the console
        """

        def GetFirstChild(ctrl: TreeNode) -> TreeNode:
            if isinstance(ctrl, auto.TreeItemControl):
                ecpt = ctrl.GetExpandCollapsePattern()
                if (
                    ecpt
                    and ecpt.ExpandCollapseState == auto.ExpandCollapseState.Expanded
                ):
                    child = None
                    tryCount = 0
                    # some tree items need some time to finish expanding
                    while not child:
                        tryCount += 1
                        child = ctrl.GetFirstChildControl()
                        if child or tryCount > 20:
                            break
                        time.sleep(0.05)
                    return child
            else:
                return ctrl.GetFirstChildControl()

        def GetNextSibling(ctrl: TreeNode) -> TreeNode:
            return ctrl.GetNextSiblingControl()

        index = 1
        target_elem = self.ctx.get_element(locator)
        image_folder = None
        elements = []
        if capture_image_folder:
            image_folder = Path(capture_image_folder).expanduser().resolve()
            image_folder.mkdir(parents=True, exist_ok=True)
        control_log = self.logger.warning if log_as_warnings else self.logger.info

        for control, depth in auto.WalkTree(
            target_elem.item,
            getFirstChild=GetFirstChild,
            getNextSibling=GetNextSibling,
            includeTop=True,
            maxDepth=max_depth,
        ):
            control_str = str(control)
            if image_folder:
                capture_filename = f"{control.ControlType}_{index}.png"
                img_path = str(image_folder / capture_filename)
                try:
                    control.CaptureToImage(img_path)
                except Exception as exc:  # pylint: disable=broad-except
                    self.logger.warning(
                        "Couldn't capture into %r due to: %s", img_path, exc
                    )
                else:
                    control_str += f" [{capture_filename}]"
            control_log(" " * depth * 4 + control_str)
            elements.append({"depth": depth, "control": control})
            index += 1

        return elements
