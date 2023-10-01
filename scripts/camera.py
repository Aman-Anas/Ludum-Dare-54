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
        target = own.parent
        camPos: KX_GameObject = own.scene.objects["cameraPosition"]

        cast = camPos.rayCast(target, dist=camPos.getDistanceTo(target))
        if cast[0]:
            if cast[0].name == "ship":
                own.worldPosition = camPos.worldPosition
            else:
                hitPoint = cast[1]
                own.worldPosition = hitPoint
