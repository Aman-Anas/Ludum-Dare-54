from bge.types import KX_GameObject, KX_Scene


class ObjectPool:
    def __init__(self, scene: KX_Scene, reference: KX_GameObject,
                 objName: str, maxSize: int, inactivePosition: float | None = None,
                 duplicateMesh: bool = False, usePhysics: bool = False) -> None:
        self.scene = scene
        self.objName = objName
        self.reference = reference

        # Flags
        self.inactivePosition = inactivePosition
        self.duplicateMesh = duplicateMesh
        self.usePhysics = usePhysics

        self.currentPoolID = 0

        self.activeObjects: dict[int, KX_GameObject] = {}
        self.freeObjects: list[KX_GameObject] = []

        self.maxSize = maxSize

    def getObject(self) -> KX_GameObject:
        if len(self.freeObjects) < 1:
            newObj = self.scene.addObject(self.objName, self.reference, 0.0)
            newObj["pool"] = self
            newObj["poolID"] = self.currentPoolID
            self.currentPoolID += 1

            if self.duplicateMesh:
                newMesh = newObj.meshes[0].copy()
                newObj.replaceMesh(newMesh, True, True)

        else:
            newObj = self.freeObjects.pop()
            if newObj.invalid:
                return self.getObject()

            if self.usePhysics:
                newObj.restorePhysics()

        self.activeObjects[newObj["poolID"]] = newObj

        return newObj

    def removeObject(self, obj: KX_GameObject):

        del self.activeObjects[obj["poolID"]]

        if len(self.freeObjects) < self.maxSize:
            if self.inactivePosition is not None:
                obj.worldPosition.z = self.inactivePosition

            if self.usePhysics:
                obj.suspendPhysics()

            self.freeObjects.append(obj)

        else:
            obj.endObject()
