import bge
from bge.types import SCA_PythonController


ROTATE_FAC = 0.1
ORIENT_MOVE_FACTOR = 90.0
ROLL_FACTOR = 2.0
THROTTLE_RAMP = 1.0
THROTTLE_FAC = 3.2
MAX_ROT_VELO = 6.2
MAX_MOVEMENT_SPEED = 60.0
SLOW_DOWN_SPEED = 2.0

mouse = bge.logic.mouse
keyboard = bge.logic.keyboard


def movement(cont: SCA_PythonController):
    if cont.sensors["loop"].positive:
        own = cont.owner
        target = own.scene.objects["lookTarget"]
        model = own.children["model"]

        tarVec = own.getVectTo(target)[1]
        own.lookAt(tarVec, 1, ROTATE_FAC)

        keyMap = bge.logic.globalDict["key_map"]
        config = bge.logic.globalDict["config"]

        mouseDelta = mouse.deltaPosition
        # ship.applyRotation([0, 0, mouseDelta[0]], True)
        # zVec = Vector([0, 0, mouseDelta[0]])
        # ship.applyTorque(zVec, True)
        # ship.applyRotation([mouseDelta[1], 0, 0], True)
        own.localAngularVelocity.z = max(
            min(mouseDelta[0] * ORIENT_MOVE_FACTOR * config["MOUSE_SENSITIVITY"], MAX_ROT_VELO), -MAX_ROT_VELO)

        if config["DIRECTION"]:
            xMouse = -mouseDelta[1]
        else:
            xMouse = mouseDelta[1]

        own.localAngularVelocity.x = max(
            min(xMouse * ORIENT_MOVE_FACTOR * config["MOUSE_SENSITIVITY"], MAX_ROT_VELO), -MAX_ROT_VELO)

        mouse.reCenter()

        right = False
        left = False

        activeInputs = keyboard.activeInputs
        if keyMap["roll_left"] in activeInputs:
            own.localAngularVelocity.y -= ROLL_FACTOR
            left = True
        if keyMap["roll_right"] in activeInputs:
            own.localAngularVelocity.y += ROLL_FACTOR
            right = True

        if (right and left) or (not (right or left)):
            own.localAngularVelocity.y = 0

        own.localAngularVelocity.y = max(
            min(own.localAngularVelocity.y, MAX_ROT_VELO), -MAX_ROT_VELO)

        if keyMap["throttle_up"] in activeInputs:
            own["throttle"] += THROTTLE_RAMP
        if keyMap["throttle_down"] in activeInputs:
            own["throttle"] -= THROTTLE_RAMP

        own["throttle"] = min(100, max(0, own["throttle"]))

        own.applyForce([0, own["throttle"] * THROTTLE_FAC, 0], True)

        if own.localLinearVelocity.y > 0:
            own.applyForce(
                [0, -SLOW_DOWN_SPEED * own.localLinearVelocity.y, 0], True)

        own.localLinearVelocity.y = min(
            MAX_MOVEMENT_SPEED, max(-MAX_MOVEMENT_SPEED, own.localLinearVelocity.y))

        own.localLinearVelocity.x = 0
        own.localLinearVelocity.z = 0
        model["frame"] = own["throttle"]
