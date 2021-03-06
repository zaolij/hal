from config import get_hal
import internet
from light_stairs import illuminate_stairs
from time import sleep
import os

hal = get_hal()
log = hal.getLogger(__name__)


def open_hs(called_on_trigger):
    log.info("OPEN the hackerspace")
    for anim in ("red", "green", "blue", "kitchen", "belgatop"):
        hal.upload(anim, hal.sinusoid(250, 0, 200))
        hal.loop(anim)
        hal.play(anim)
        hal.fps(anim, 50)
        sleep(0.0001)

    hal.upload("bell_eyes", [255])
    hal.play("bell_eyes")
    hal.one_shot("door_green")
    hal.play("heater")
    for switch in ("power", "leds_stairs", "ampli", "belgaleft", "belgaright"):
        hal.on(switch)
    hal.off("knife_r")
    hal.off("knife_b")
    hal.on("knife_g")

    if called_on_trigger and not internet.spaceapi_isopen():
        internet.lechbot_event('hs_open')
        internet.spaceapi_open()
        internet.events.send('hs_open', ["open", "status"])


def close_hs(called_on_trigger):
    log.info("CLOSE the hackerspace")
    if called_on_trigger:
        internet.lechbot_event('hs_close')

    os.system("mpc pause")
    
    hal.off("ampli")
    hal.on("knife_r")
    hal.off("knife_b")
    hal.off("knife_g")

    # Shotdown all leds
    for anim in ("red", "green", "blue", "heater", "door_green", "kitchen", "roof_g", "roof_b", "roof_r"):
        hal.stop(anim)
        sleep(0.0001)

    if called_on_trigger and internet.spaceapi_isopen():
        illuminate_stairs()
        internet.spaceapi_close()
        internet.events.send("hs_close", ["close", "status"])
        for i in range(3):
            hal.on("belgaleft")
            hal.off("belgaright")
            sleep(1)
            hal.off("belgaleft")
            hal.on("belgaright")
            sleep(1)


    hal.stop("bell_eyes")


def main():
    if hal.trig("knife_switch"):
        open_hs(called_on_trigger=False)
    else:
        close_hs(called_on_trigger=False)

    for trigger_name, state in hal.events():
        if trigger_name != 'knife_switch':
            continue

        if state is True:
            open_hs(called_on_trigger=True)
        else:
            close_hs(called_on_trigger=True)


if __name__ == "__main__":
    main()
