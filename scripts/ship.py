import bge
from bge.types import SCA_PythonController
import aud
from threading import Thread

from .pool import ObjectPool

ROTATE_FAC = 0.1
ORIENT_MOVE_FACTOR = 90.0
ROLL_FACTOR = 2.0
THROTTLE_RAMP = 1.0
THROTTLE_FAC = 2.2
MAX_ROT_VELO = 6.2
MAX_MOVEMENT_SPEED = 200.0  # 40.0
SLOW_DOWN_SPEED = 2.0

mouse = bge.logic.mouse
keyboard = bge.logic.keyboard


def playSound(path, scene, obj=None, max_distance=10):
    """ Play 3D sound from path in the position of given object.
    Remember that 3D sound only works with mono audio files. """

    # Get the audio device and set its properties according to current camera
    if "sound_device" not in bge.logic.globalDict:
        bge.logic.globalDict["sound_device"] = aud.device()

    device = bge.logic.globalDict["sound_device"]

    # Create an audio factory and play it, with a handle as result

    if "sound_lib" not in bge.logic.globalDict:
        bge.logic.globalDict["sound_lib"] = {}

    soundLib = bge.logic.globalDict["sound_lib"]

    if path not in soundLib:
        sound = aud.Factory(path)
        sound.buffer()
        soundLib[path] = sound

    bufferedSound = soundLib[path]
    handle = device.play(bufferedSound)

    if obj is not None:
        device.distance_model = aud.AUD_DISTANCE_MODEL_LINEAR
        device.listener_location = scene.active_camera.worldPosition
        device.listener_orientation = scene.active_camera.worldOrientation.to_quaternion()

        # Makes the handle behave as a 3D sound
        handle.relative = False
        handle.location = obj.worldPosition

        # If sound source is farther from listener than the value below, volume is zero
        handle.distance_maximum = max_distance


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

        activeInputs = {**keyboard.activeInputs, **mouse.activeInputs}
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

        nose = cont.sensors["nose"]

        if not nose.positive:
            own.applyForce([0, own["throttle"] * THROTTLE_FAC, 0], True)

        if own.localLinearVelocity.y > 0:
            own.applyForce(
                [0, -SLOW_DOWN_SPEED * own.localLinearVelocity.y, 0], True)

        own.localLinearVelocity.y = min(
            MAX_MOVEMENT_SPEED, max(-MAX_MOVEMENT_SPEED, own.localLinearVelocity.y))

        own.localLinearVelocity.x = 0
        own.localLinearVelocity.z = 0
        model["frame"] = own["throttle"]


def shoot(cont: SCA_PythonController):
    if cont.sensors["loop"].positive:
        own = cont.owner

        if "init" not in own:
            own["pool"] = ObjectPool(
                own.scene, own, "GoodLaser", 20, -200, usePhysics=True)
            own["init"] = True

        pool: ObjectPool = own["pool"]

        keyMap = bge.logic.globalDict["key_map"]
        activeInputs = {**keyboard.activeInputs, **mouse.activeInputs}

        if (keyMap["shoot"] in activeInputs) and (own["cool"] > 0.1):
            own["cool"] = 0.0
            obj = pool.getObject()
            obj.localLinearVelocity.x = 0
            obj.localLinearVelocity.y = 0
            obj.setAngularVelocity([0, 0, 0], True)
            obj.worldPosition = own.worldPosition
            obj.worldOrientation = own.worldOrientation
            obj.localLinearVelocity.y = 200
            path_to_shoot = bge.logic.expandPath(
                "//assets/sound/Spaceship_Shoot.mp3")
            # playSound(path_to_shoot, own.scene)


def removeBullet(cont: SCA_PythonController):
    if cont.sensors["Delay"].positive or cont.sensors["Collision"].positive:
        own = cont.owner

        pool: ObjectPool = own["pool"]
        if own["poolID"] in pool.activeObjects:
            pool.removeObject(own)


def hurt(cont: SCA_PythonController):
    if cont.sensors["hurt"].positive or cont.sensors["lava"].positive:
        own = cont.owner
        own["health"] -= 5
        if cont.sensors["lava"].positive:
            own["health"] -= 6

        overlay = bge.logic.getSceneList()["overlay"]
        plane = overlay.objects["HurtPlane"]
        plane["hurt"] = True

        if own["health"] <= 0:
            bge.logic.levelManager.respawn()


def nextLevel(cont: SCA_PythonController):
    if cont.sensors["next"].positive:
        bge.logic.levelManager.loadNextLevel()
