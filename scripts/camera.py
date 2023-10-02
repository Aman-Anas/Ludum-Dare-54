import bge
from bge.types import SCA_PythonController, KX_GameObject
from mathutils import Vector

POS_LERP_FACTOR = 0.1
ROT_SLERP_FACTOR = 0.1


def followShip(cont: SCA_PythonController):
    if cont.sensors["loop"].positive:
        own = cont.owner
        ship: KX_GameObject = own.scene.objects["ship"]

        shipPos = ship.worldPosition

        own.worldPosition = shipPos.lerp(own.worldPosition, POS_LERP_FACTOR)

        curOrient = own.worldOrientation.to_quaternion()
        shipOrient = ship.worldOrientation.to_quaternion()

        own.worldOrientation = curOrient.slerp(shipOrient, ROT_SLERP_FACTOR)


def collide(cont: SCA_PythonController):
    if cont.sensors["loop"].positive:
        own = cont.owner
        parent = own.parent
        target = own.scene.objects["cameraTarget"]
        ship: KX_GameObject = own.scene.objects["ship"]
        camPos: KX_GameObject = own.scene.objects["cameraPosition"]

        cast = ship.rayCast(camPos, dist=(camPos.getDistanceTo(target)))
        if cast[0]:
            hitPoint = cast[1]
            parent.worldPosition = hitPoint
        else:
            parent.worldPosition = camPos.worldPosition
