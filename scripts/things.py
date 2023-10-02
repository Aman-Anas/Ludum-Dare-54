from bge.types import KX_GameObject, SCA_PythonController


def runLevelThingy(cont: SCA_PythonController):
    if cont.sensors["loop"].positive:
        own = cont.owner
        count = 0
        for obj in own.children:
            if "switched" in obj:
                if obj["switched"]:
                    count += 1

        if count >= 10:
            obj = own.scene.addObject(
                own.scene.objectsInactive["NextLevelThing"], own, 0.0)
            obj.worldPosition = own.worldPosition
            own.endObject()
