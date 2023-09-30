from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING
import sys

from .bgimgui import widgets

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

        imgui.text("Logic Tick Rate (FPS)")
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
        allInputs = {**keyboard.activeInputs}  # , **mouse.activeInputs}
        keyMap = bge.logic.globalDict["key_map"]

        imgui.text("Enter a key...")  # or mouse button...")

        if len(allInputs) > 0:
            activeInput = list(allInputs)[0]
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
        settings = imgui.button("Open Settings", -1)

        if settings:
            self.gui.settingsWindow.setVisible(True)

        exitGame = imgui.button("Exit Game", -1)

        if exitGame:
            bge.logic.endGame()
