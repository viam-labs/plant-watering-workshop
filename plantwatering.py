import asyncio
import os

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.board import Board

# Set GPIO pin numbers
MOISTURE_PIN = '40' # Change this to the actual GPIO pin number connected to the moisture sensor
RELAY_PIN = '8' # Change this to the actual GPIO pin number connected to the relay

robot_secret = os.getenv('ROBOT_SECRET') or ''
robot_address = os.getenv('ROBOT_ADDRESS') or ''

async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload=robot_secret)
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address(robot_address, opts)

async def moisture_loop(board):
    '''
    moisture_pin value:
    - high: no moisture (True)
    - low: means there is moisture (False)
    '''
    # Main program loop, with relay pin
    moisture_pin = await board.gpio_pin_by_name(MOISTURE_PIN)
    relay_pin = await board.gpio_pin_by_name(RELAY_PIN)
    detect_moisture = await moisture_pin.get()
    
    # debug
    print(f'moisture_loop: {MOISTURE_PIN}:{detect_moisture}')
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

    print('Resources:')
    print(robot.resource_names)
    
    # pi/board
    pi = Board.from_robot(robot, "pi")
    # replace placeholder pin with valid 
    pi_return_value = await pi.gpio_pin_by_name("8")
    print(f"pi gpio_pin_by_name return value: {await pi_return_value.get()}")
    
    # change the sync based on longer times 
    watering_sleep = 1
    while True:
        running = await moisture_loop(pi)
        if running:
            # you can sleep for 5 seconds (depending on size of pot)
            print('relay running')
        else:
            print('relay not running')
        await asyncio.sleep(watering_sleep)
    
    # Don't forget to close the robot when you're done!
    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
