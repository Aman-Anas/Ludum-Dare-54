import os

from .bgimgui import BGEImguiWrapper, styleGUI
from . import windows
from .windows import GUIModes

import imgui
import bge
from bge.types import KX_Scene
import orjson

DEFAULT_KEY_MAP = {
    "roll_right": "DKEY",
    "roll_left": "AKEY",
    "throttle_up": "WKEY",
    "throttle_down": "SKEY",
    "shoot": "LEFTMOUSE"
}

DEFAULT_CONFIG = {
    "DIRECTION": False,
    "MOUSE_SENSITIVITY": 1.0
}


def getAssetDir():
    return bge.logic.expandPath("//assets/\\")


configFileStr = f"{getAssetDir()}config.json"


def loadConfig():
    if os.path.isfile(configFileStr):
        with open(configFileStr, 'rb') as openfile:
            data = orjson.loads(openfile.read())

    # If no key map config file exists, make a default one
    else:
        data = {}
        data["key_map"] = DEFAULT_KEY_MAP
        data["config"] = DEFAULT_CONFIG

        jsonData = orjson.dumps(
            data, option=orjson.OPT_INDENT_2)
        with open(configFileStr, 'wb') as outfile:
            outfile.write(jsonData)

    bge.logic.globalDict["key_map"] = {}
    bge.logic.globalDict["config"] = {}

    keyMapValues = data["key_map"]

    for strKey in keyMapValues:
        bge.logic.globalDict["key_map"][strKey] = getattr(
            bge.events, keyMapValues[strKey])

    configValues = data["config"]
    bge.logic.globalDict["config"] = configValues


def saveConfig():
    keyMap = bge.logic.globalDict["key_map"]
    config = bge.logic.globalDict["config"]

    keyMapValues = {}
    for key in keyMap:
        stringName = bge.events.EventToString(keyMap[key])
        keyMapValues[key] = stringName

    data = {}
    data["key_map"] = keyMapValues
    data["config"] = config

    jsonData = orjson.dumps(
        data, option=orjson.OPT_INDENT_2)
    with open(configFileStr, 'wb') as outfile:
        outfile.write(jsonData)


class MainGameGUI(BGEImguiWrapper):
    # Example class for how you would override and make your own GUI
    def __init__(self, scene: KX_Scene, cursorPath=None) -> None:
        imgui.load_ini_settings_from_disk("")

        self.pause = False
        cursorPath = f"{getAssetDir()}/cursors"
        bge.logic.levelManager = None

        self.mode = GUIModes.TITLE_SCREEN

        super().__init__(scene, cursorPath)

    def initializeGUI(self):
        super().initializeGUI()

        io = imgui.get_io()
        self.io = io

        # allow user to navigate UI with a keyboard
        io.config_flags |= imgui.CONFIG_NAV_ENABLE_KEYBOARD
        self.savedMousePos = self.imgui_backend.mouse.position
        styleConfigPath = f"{getAssetDir()}ui_style.toml"
        styleGUI(styleConfigPath)

        loadConfig()

        backend = self.imgui_backend

        font_global_scaling_factor = 2  # Set to 2 for high res displays?
        backend.setScalingFactors(font_global_scaling_factor, 1.4)

        mainFontPath = bge.logic.expandPath("//assets/fonts/main.ttf")
        mainFont = backend.setMainFont(mainFontPath, 11)

        iconFontPath = bge.logic.expandPath("//assets/fonts/icons.ttf")
        customGlyphStart = ord("\ue900")
        customGlyphEnd = ord("\uEAEE")
        customGlyphRange = imgui.GlyphRanges(
            [customGlyphStart, customGlyphEnd, 0])

        config = imgui.core.FontConfig(merge_mode=False)

        iconFont = backend.addExtraFont(
            iconFontPath, 18, font_config=config, glyph_ranges=customGlyphRange)

        self.mainFont = mainFont
        self.iconFont = iconFont

        self.activeSceneName = "title"
        self.pause = False

        # Add window objects
        self.settingsWindow = windows.SettingsWindow(io, self)

        self.pauseWindow = windows.PauseWindow(io, self)

        self.startWindow = windows.StartPanel(io, self)

        self.helpWindow = windows.HelpWindow(io)

        self.setupMainGUIWindows(io)

    def setupMainGUIWindows(self, io):
        self.throttle = windows.ThrottleWindow(io, self)
        self.health = windows.HealthBar(io, self)
        self.timer = windows.TimerWindow(io, self)

    def drawMainGUI(self):
        self.pauseWindow.drawWindow()
        self.settingsWindow.drawWindow()
        self.throttle.drawWindow()
        self.health.drawWindow()
        self.helpWindow.drawWindow()
        self.timer.drawWindow()

    def updateSceneName(self, name: str):
        self.activeSceneName = name

    def togglePause(self):
        sceneStr = self.activeSceneName
        scene: KX_Scene = bge.logic.getSceneList()[sceneStr]

        inGame = self.mode is GUIModes.MAIN_GAME

        if not self.pause:
            scene.suspend()
            self.pauseWindow.setVisible(True)
            self.pause = True

            if inGame:
                self.showCursor = True

        else:
            scene.resume()
            self.pauseWindow.setVisible(False)
            self.settingsWindow.setVisible(False)
            self.pause = False

            if inGame:
                self.showCursor = False

    def drawGUI(self):
        backend = self.imgui_backend

        # Draw Menu Bar
        # if imgui.begin_main_menu_bar():
        #     if imgui.begin_menu("File", True):

        #         clicked_quit, selected_quit = imgui.menu_item(
        #             "Quit", "Cmd+Q", False, True
        #         )

        #         if clicked_quit:
        #             sys.exit(0)

        #         imgui.end_menu()
        #     imgui.end_main_menu_bar()

        # Draws all of the added window objects
        super().drawGUI()

        screenWidth, screenHeight = backend.getScreenSize()

        match self.mode:
            case GUIModes.TITLE_SCREEN:
                self.pauseWindow.drawWindow()
                self.settingsWindow.drawWindow()
                self.startWindow.drawWindow()
                self.helpWindow.drawWindow()

            case GUIModes.MAIN_GAME:
                self.drawMainGUI()
            case _:
                pass

    def saveKeys(self):
        saveConfig()
