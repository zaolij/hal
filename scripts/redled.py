#!/usr/bin/python

from config import get_hal
import internet
from math import log
from time import sleep

hal = get_hal()
logger = hal.getLogger(__name__)

def n_people():
    macs = None
    try:
        macs = internet.pamela()
    except:
        logger.warning("Error when retrieving pamela's MAC.json")
        pass
    if macs:
        return len(macs["color"]) + len(macs["grey"])
    return 0


def main():
    hal.upload("red", hal.sinusoid(val_max=0.75))
    hal.loop("red")
    hal.play("red")
    last_fps = -1
    while True:
        n = n_people()
        fps = 25*log(2+n)
        if fps != last_fps:
            hal.fps("red", fps)
            logger.info("Set red ledstrip to %d FPS (%d people)" % (fps, n))
            last_fps = fps
        sleep(10)


if __name__ == "__main__":
    main()
