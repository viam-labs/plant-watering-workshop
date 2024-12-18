import asyncio
import os

from viam.robot.client import RobotClient
from viam.components.board import Board

# Set GPIO pin numbers
MOISTURE_PIN = (
    "40"  # Change this to the actual GPIO pin number connected to the moisture sensor
)
RELAY_PIN = "8"  # Change this to the actual GPIO pin number connected to the relay

BOARD_NAME = os.getenv("BOARD_NAME") or "board-1"
ROBOT_API_KEY = os.getenv("ROBOT_API_KEY") or "PUT ROBOT API KEY HERE"
ROBOT_API_KEY_ID = os.getenv("ROBOT_API_KEY_ID") or "PUT ROBOT API KEY ID HERE"
ROBOT_ADDRESS = os.getenv("ROBOT_ADDRESS") or "PUT ROBOT ADDRESS HERE"


async def connect():
    opts = RobotClient.Options.with_api_key(
        api_key=ROBOT_API_KEY, api_key_id=ROBOT_API_KEY_ID
    )
    return await RobotClient.at_address(ROBOT_ADDRESS, opts)


async def moisture_loop(board):
    """
    moisture_pin value:
    - high: no moisture (True)
    - low: means there is moisture (False)
    """
    # Main program loop, with relay pin
    moisture_pin = await board.gpio_pin_by_name(MOISTURE_PIN)
    relay_pin = await board.gpio_pin_by_name(RELAY_PIN)
    detect_moisture = await moisture_pin.get()

    # debug
    print(f"moisture_loop: {MOISTURE_PIN}:{detect_moisture}")
    if detect_moisture == True:
        # start the relay
        await relay_pin.set(True)
    else:
        # stop the relay
        await relay_pin.set(False)

    # return the status of the relay
    return await relay_pin.get()


async def main():
    robot = await connect()

    print("Resources:")
    print(robot.resource_names)

    # pi/board
    pi = Board.from_robot(robot, BOARD_NAME)

    # change the sync based on longer times
    watering_sleep = 1
    while True:
        running = await moisture_loop(pi)
        if running:
            # you can sleep for 5 seconds (depending on size of pot)
            print("relay running")
        else:
            print("relay not running")
        await asyncio.sleep(watering_sleep)

    # Don't forget to close the robot when you're done!
    await robot.close()


if __name__ == "__main__":
    asyncio.run(main())
