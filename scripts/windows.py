from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING
import sys

from .bgimgui import widgets
from .levels import LevelManager

import imgui
import bge

if TYPE_CHECKING:
    from .gui import MainGameGUI

mouse = bge.logic.mouse
keyboard = bge.logic.keyboard


class GUIModes(Enum):
    TITLE_SCREEN = 0
    MAIN_GAME = 1


class SettingsWindow(widgets.GUIWindow):

    START_DEBUG = True

    def __init__(self, io: imgui._IO, gui: MainGameGUI, extraFlags=None) -> None:
        super().__init__("Settings", io, True, extraFlags)
        self.gui = gui
        self.setVisible(False)

        self.showDebug = SettingsWindow.START_DEBUG

        self.updateValues()

        self.controlCaptureMode = False
        self.controlValue = None

    def updateValues(self):
        self.resolution = (bge.render.getWindowWidth(),
                           bge.render.getWindowHeight())
        self.fullscreen = bge.render.getFullScreen()

        self.maxLogicFrame = bge.logic.getMaxLogicFrame()
        self.logicTickRate = bge.logic.getLogicTicRate()

        self.vsyncOptions = ["VSYNC OFF", "VSYNC ADAPTIVE", "VSYNC ON"]
        self.vsyncEnums = [bge.render.VSYNC_OFF,
                           bge.render.VSYNC_ADAPTIVE, bge.render.VSYNC_ON]

        self.vsync = bge.render.getVsync()
        self.vsyncOptionIndex = self.vsyncEnums.index(self.vsync)

    def drawContents(self):

        imgui.separator()
        with imgui.begin_tab_bar("SettingsTabs") as tab_bar:
            if tab_bar.opened:
                with imgui.begin_tab_item("General") as general:
                    if general.selected:
                        self.drawGeneralSettings()

                with imgui.begin_tab_item("Controls") as controls:
                    if controls.selected:
                        if self.controlCaptureMode:
                            self.captureControls()
                        else:
                            self.drawControlSettings()

    def drawGeneralSettings(self):
        refresh = imgui.button("Refresh settings after window resize")

        imgui.separator()

        maxResolution = bge.render.getDisplayDimensions()
        imgui.text("Resolution")
        imgui.text(
            f"Detected max display resolution: {maxResolution}")
        _, self.resolution = imgui.input_int2(
            "##resolution", *self.resolution)

        imgui.text("Fullscreen: ")
        imgui.same_line()
        _, self.fullscreen = imgui.checkbox("##fullscreen", self.fullscreen)

        imgui.separator()

        imgui.text("Maximum Logic Frames per second")
        _, self.maxLogicFrame = imgui.input_int(
            "##maxLogicFrames", self.maxLogicFrame)

        imgui.text("Logic Tick Rate (FPS) [BUGGY, use 60fps]")
        _, self.logicTickRate = imgui.input_float(
            "##logicTickRate", self.logicTickRate)

        imgui.text("V-Sync setting")
        _, self.vsyncOptionIndex = imgui.combo(
            "##Vsyncsetting", self.vsyncOptionIndex, self.vsyncOptions)

        imgui.separator()

        imgui.text("Show debug info: ")
        imgui.same_line()
        _, self.showDebug = imgui.checkbox("##debugInfo", self.showDebug)

        apply = imgui.button("Apply settings!", -1)

        if apply:
            bge.logic.setMaxLogicFrame(self.maxLogicFrame)
            bge.logic.setLogicTicRate(self.logicTickRate)
            bge.logic.setPhysicsTicRate(self.logicTickRate)
            bge.render.setFullScreen(self.fullscreen)
            bge.render.setWindowSize(*self.resolution)

            bge.render.showFramerate(self.showDebug)
            bge.render.showProfile(self.showDebug)
            bge.render.showProperties(self.showDebug)

            bge.render.setVsync(self.vsyncEnums[self.vsyncOptionIndex])

        if refresh:
            self.updateValues()

    def captureControls(self):
        if self.controlValue is None:
            self.controlCaptureMode = False
            return

        # Put all active inputs in one dictionary
        allInputs = {**keyboard.activeInputs, **mouse.activeInputs}
        keyMap = bge.logic.globalDict["key_map"]

        imgui.text("Enter a key or mouse button...")

        if len(allInputs) > 0:
            activeInput = list(allInputs)[0]
            if (activeInput != bge.events.MOUSEX) and (activeInput != bge.events.MOUSEY):
                keyMap[self.controlValue] = activeInput
                self.controlCaptureMode = False

    def drawControlSettings(self):
        imgui.text("Set keys")
        imgui.separator()
        keyMap = bge.logic.globalDict["key_map"]
        for key in keyMap:
            if imgui.button(f"Set {key}"):
                self.controlCaptureMode = True
                self.controlValue = key
            imgui.same_line()

            stringName = bge.events.EventToString(keyMap[key])

            with imgui.font(self.gui.iconFont):
                if ("MOUSEX" in stringName):
                    if imgui.button(f"\uea7c ##{key}"):
                        keyMap[key] = bge.events.MOUSEY
                elif ("MOUSEY" in stringName):
                    if imgui.button(f"\uea7c ##{key}"):
                        keyMap[key] = bge.events.MOUSEX

            imgui.same_line()

            imgui.text(
                f"Current: {stringName}")

        _, bge.logic.globalDict["config"]["DIRECTION"] = imgui.checkbox(
            "Invert pitch axis", bge.logic.globalDict["config"]["DIRECTION"])

        _, bge.logic.globalDict["config"]["MOUSE_SENSITIVITY"] = imgui.slider_float(
            "Mouse sensitivity", bge.logic.globalDict["config"]["MOUSE_SENSITIVITY"], 0.0, 3.0)

        if imgui.button("Save settings", -1):
            self.gui.saveKeys()


class PauseWindow(widgets.GUIWindow):

    def __init__(self, io: imgui._IO, gui: MainGameGUI, flags=0) -> None:
        flags |= imgui.WINDOW_NO_COLLAPSE
        flags |= imgui.WINDOW_NO_TITLE_BAR
        flags |= imgui.WINDOW_ALWAYS_AUTO_RESIZE
        flags |= imgui.WINDOW_NO_RESIZE
        flags |= imgui.WINDOW_NO_MOVE
        super().__init__("Pause", io, False, flags)

        self.gui = gui

        self.setVisible(False)

    def drawWindow(self):
        display_size = self.io.display_size
        imgui.set_next_window_position(
            display_size.x * 0.5, display_size.y * 0.5, pivot_x=0.5, pivot_y=0.5)
        super().drawWindow()

    def drawContents(self):
        display_size = self.io.display_size
        imgui.dummy(display_size.x * 0.4, 0)
        imgui.push_style_color(imgui.COLOR_BUTTON, 1.0, 0.0, 0.3529)
        helpMenu = imgui.button("Help!", -1)
        imgui.pop_style_color(1)

        if helpMenu:
            self.gui.helpWindow.setVisible(True)

        settings = imgui.button("Open Settings", -1)

        if settings:
            self.gui.settingsWindow.setVisible(True)

        title = imgui.button("Return to Title", -1)
        if title:
            bge.logic.restartGame()

        exitGame = imgui.button("Exit Game", -1)

        if exitGame:
            bge.logic.endGame()


class StartPanel(widgets.GUIWindow):
    def __init__(self, io: imgui._IO, gui: MainGameGUI, flags=0) -> None:
        flags |= imgui.WINDOW_NO_COLLAPSE
        flags |= imgui.WINDOW_NO_TITLE_BAR
        flags |= imgui.WINDOW_NO_RESIZE
        flags |= imgui.WINDOW_NO_MOVE
        flags |= imgui.WINDOW_NO_BACKGROUND

        super().__init__("StartPanel", io, False, flags)
        self.setVisible(True)
        self.gui = gui

    def drawWindow(self):
        display_size = self.io.display_size
        imgui.set_next_window_size(display_size.x * 0.25, display_size.y * 0.6)
        imgui.set_next_window_position(
            display_size.x * 0.5, display_size.y * 0.7, pivot_x=0.5, pivot_y=0.5)
        super().drawWindow()

    def drawContents(self):

        if imgui.button("Start", -1):
            scene = bge.logic.getSceneList()["title"]
            scene.replace("game")
            self.gui.updateSceneName("game")
            self.gui.mode = GUIModes.MAIN_GAME
            self.gui.showCursor = False

        if imgui.button("Help", -1):
            self.gui.helpWindow.setVisible(True)

        if imgui.button("Settings", -1):
            if not self.gui.pause:
                self.gui.togglePause()
            self.gui.settingsWindow.setVisible(True)

        if imgui.button("Exit", -1):
            bge.logic.endGame()


class HelpWindow(widgets.GUIWindow):
    def __init__(self, io: imgui._IO, flags=None) -> None:
        super().__init__("Help Window", io, True, flags)
        self.setVisible(False)

    def drawContents(self):
        imgui.text("Help text goes here!")
        imgui.separator()
        imgui.text("Current controls:")
        keymap = bge.logic.globalDict["key_map"]
        for key in keymap:
            keyName = bge.events.EventToString(keymap[key])
            imgui.text(f"{key} : {keyName}")


class ThrottleWindow(widgets.GUIWindow):
    def __init__(self, io: imgui._IO, gui: MainGameGUI, flags=0) -> None:
        flags |= imgui.WINDOW_NO_COLLAPSE
        flags |= imgui.WINDOW_NO_TITLE_BAR
        flags |= imgui.WINDOW_NO_RESIZE
        flags |= imgui.WINDOW_NO_MOVE
        flags |= imgui.WINDOW_NO_BACKGROUND
        flags |= imgui.WINDOW_ALWAYS_AUTO_RESIZE

        super().__init__("Throttle", io, False, flags)
        self.setVisible(True)
        self.gui = gui

    def drawWindow(self):
        display_size = self.io.display_size
        # imgui.set_next_window_size(
        #     display_size.x * 0.15, display_size.y * 0.10)
        imgui.set_next_window_position(
            display_size.x * 1.0, display_size.y * 1.0, pivot_x=1.0, pivot_y=1.0)
        super().drawWindow()

    def drawContents(self):
        imgui.text("esc to view help")


class HealthBar(widgets.GUIWindow):
    def __init__(self, io: imgui._IO, gui: MainGameGUI, flags=0) -> None:
        flags |= imgui.WINDOW_NO_COLLAPSE
        flags |= imgui.WINDOW_NO_TITLE_BAR
        flags |= imgui.WINDOW_NO_RESIZE
        flags |= imgui.WINDOW_NO_MOVE
        flags |= imgui.WINDOW_NO_BACKGROUND
        flags |= imgui.WINDOW_ALWAYS_AUTO_RESIZE

        super().__init__("Health", io, False, flags)
        self.setVisible(True)
        self.gui = gui

    def drawWindow(self):
        display_size = self.io.display_size
        # imgui.set_next_window_size(
        #     display_size.x * 0.15, display_size.y * 0.10)
        imgui.set_next_window_position(
            display_size.x * 1.0, display_size.y * 0.0, pivot_x=1.0, pivot_y=0.0)
        super().drawWindow()

    def drawContents(self):
        mainScene = bge.logic.getSceneList()["game"]
        ship = mainScene.objects["ship"]
        imgui.push_style_color(imgui.COLOR_PLOT_HISTOGRAM, 1.0, 0.0, 0.3529)
        imgui.progress_bar(ship["health"] / 100.0, (200, 20), "Health")
        imgui.pop_style_color(1)
        # mainScene = bge.logic.getSceneList()["game"]
        # ship = mainScene.objects["ship"]
        imgui.progress_bar(ship["throttle"] / 100.0, (200, 40), "Throttle")
