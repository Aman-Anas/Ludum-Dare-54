import bge
from bge.types import SCA_PythonController
from .gui import MainGameGUI


def initGame(cont: SCA_PythonController):
    if cont.sensors["tap"].positive:
        own = cont.owner
        if "overlay" not in bge.logic.getSceneList():
            bge.logic.addScene("overlay", 1)


def runGUI(cont: SCA_PythonController):
    if cont.sensors["loop"].positive:
        own = cont.owner
        scene = own.scene

        if not own["initGUI"]:
            own["gui"] = MainGameGUI(scene)
            own["initGUI"] = True
            return

        gui: MainGameGUI = bge.logic.gui
        gui.updateOnGameFrame()


def exitScreen(cont: SCA_PythonController):
    if cont.sensors["stop"].positive:
        gui: MainGameGUI = bge.logic.gui
        gui.togglePause()
