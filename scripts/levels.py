import bge
from bge.types import KX_GameObject, KX_Scene
from mathutils import Vector

PERSIST_STR = "persist"


class LevelManager:

    def __init__(self, scene: KX_Scene):
        self.currentLevel = 0
        self.gameScene = scene
        self.moveObj = scene.objects["ship"]
        bge.logic.levelManager = self
        self.loadLevel(self.currentLevel)

    def loadLevel(self, levelNumber: int):
        self.gameScene.suspend()
        previousLevel = self.currentLevel

        if previousLevel != 0:
            for entity in self.gameScene.objects:
                if entity.parent is None:
                    if PERSIST_STR not in entity:
                        entity.endObject()

            prevLevelOriginName = f"level_{previousLevel}"
            prevLevelOrigin: KX_GameObject = self.gameScene.objects[prevLevelOriginName]
            prevLevelOrigin.endObject()

        nextLevel = levelNumber

        nextLevelOriginName = f"level_{nextLevel}"
        nextLevelOrigin: KX_GameObject = self.gameScene.objectsInactive[nextLevelOriginName]

        newOrigin: KX_GameObject = self.gameScene.addObject(
            nextLevelOrigin)

        newOrigin.worldPosition = nextLevelOrigin.worldPosition
        newOrigin.worldOrientation = nextLevelOrigin.worldOrientation

        for child in newOrigin.children:
            if "spawnPoint" in child:
                spawnPoint = child
                break

        ship = self.gameScene.objects["ship"]

        ship.worldPosition = spawnPoint.worldPosition
        ship.worldOrientation = spawnPoint.worldOrientation
        ship["throttle"] = 0.0

        # Spawn in level objects/entities
        for obj in newOrigin.childrenRecursive:
            if "spawn" in obj:
                referenceObj = self.gameScene.objectsInactive[obj["spawn"]]
                newObj: KX_GameObject = self.gameScene.addObject(
                    referenceObj, obj, 0)
                newObj.worldTransform = obj.worldTransform

        self.currentLevel = levelNumber

        self.gameScene.resume()

    def respawn(self):
        self.loadLevel(self.currentLevel)

    def loadNextLevel(self):
        self.loadLevel(self.currentLevel + 1)
