# codes make you happy

import event, halo, time, mbuild
# initialize variables
background = ''
xPos = 0
yPos = 0
gameStarted = False
cursorActive = True
isCursorLightOn = True
ready = False
myShips = []
playerShootX = 0
playerShootY = 0

# Halocode starting event for the admin of the game
@event.start
def on_start():
    halo.mesh.start_group('alex')
    placeShips()
    
# Function to show a placed ship on the LED
def placeShips():
    global background, xPos, yPos, isCursorLightOn, myShips
    background = '00000000000000000000000000000000'
    while len(myShips) < 10:
        mbuild.led_panel.show_image(background, index = 1)
        mbuild.led_panel.set_pixel(xPos, yPos, isCursorLightOn, 1)
        isCursorLightOn = not isCursorLightOn
        time.sleep(0.11)

def startShoot():
    global cursorActive, gameStarted, background, isCursorLightOn, yPos, xPos
    while cursorActive and gameStarted:
        mbuild.led_panel.show_image(background, index = 1)
        mbuild.led_panel.set_pixel(xPos, yPos, isCursorLightOn, 1)
        isCursorLightOn = not isCursorLightOn
        time.sleep(0.11)


def refreshBackground():
    global background, xPos, yPos, cursorActive, playerShootX, playerShootY
    if not cursorActive:
        charIndex = getBackgroundCharIndex(playerShootX, playerShootY)
        oldChar = background[charIndex]
        numeric = int(turnDecimal(oldChar))
        if playerShootY % 4 == 0:
            numeric -= 8
        elif playerShootY % 4 == 1:
            numeric -= 4
        elif playerShootY % 4 == 2:
            numeric -= 2
        elif playerShootY % 4 == 3:
            numeric -= 1
        newChar = str(turnHexaDecimal(numeric))
        background = background[:charIndex] + newChar + background[charIndex+1:]
    elif not gameStarted:
        charIndex = getBackgroundCharIndex(xPos, yPos)
        oldChar = background[charIndex]
        numeric = int(turnDecimal(oldChar))
        if yPos % 4 == 0:
            numeric += 8
        elif yPos % 4 == 1:
            numeric += 4
        elif yPos % 4 == 2:
            numeric += 2
        elif yPos % 4 == 3:
            numeric += 1
        newChar = str(turnHexaDecimal(numeric))
        background = background[:charIndex] + newChar + background[charIndex+1:]
        mbuild.led_panel.show_image(background, index = 1)
        
def getBackgroundCharIndex(x, y):
    index = x * 2
    if y > 3:
        index += 1
    return index

#       MOVING EVENTS
##########################################################################################
#goUp
@event.touchpad3_active
def on_3_active():
    global yPos, cursorActive
    if not cursorActive:
        return
    if yPos == 0:
        yPos = 7
    else:
        yPos -= 1

#goRight
@event.touchpad2_active
def on_2_active():
    global xPos, cursorActive
    if not cursorActive:
        return
    if xPos == 15:
        xPos = 0
    else:
        xPos += 1

#goDown
@event.touchpad1_active
def on_1_active():
    global yPos, cursorActive
    if not cursorActive:
        return
    if yPos == 7:
        yPos = 0
    else:
        yPos += 1

#goLeft
@event.touchpad0_active
def on_0_active():
    global xPos, cursorActive
    if not cursorActive:
        return
    if xPos == 0:
        xPos = 15
    else:
        xPos -= 1

#       EVENT HANDLING
##########################################################################################

#   Event to handle the buttonpress on Halocode
#
#   1. Its your turn and you can place a shot
#   2. The game hasnt started yet, so youre placing ships
@event.button_pressed
def on_button_pressed():
    global xPos, yPos, background, myShips, gameStarted, cursorActive, isCursorLightOn, ready
    if gameStarted and cursorActive:
        cursorActive = False
        mbuild.led_panel.show_image(background, index = 1)
        halo.mesh.broadcast('shoot_x', xPos)
        halo.mesh.broadcast('shoot_y', yPos)
    elif cursorActive:
        #place ship
        if ((xPos, yPos) in myShips):
            return
        myShips.append((xPos, yPos))
        refreshBackground()
        if (len(myShips) == 10):
            cursorActive = False
            isCursorLightOn = False
            ready = True
            halo.mesh.broadcast('ready')
            return

@event.mesh_message('game_start')
def on_mesh_message():
    global gameStarted, cursorActive
    print('game started now')
    gameStarted = True
    cursorActive = True
    startShoot()

# Save x position of the shot from an enemy
@event.mesh_message('shoot_x')
def on_mesh_message():
    global playerShootX
    playerShootX = halo.mesh.get_info('shoot_x')

# Save y position of the shot from an enemy
@event.mesh_message('shoot_y')
def on_mesh_message():
    global playerShootY
    playerShootY = halo.mesh.get_info('shoot_y')
    checkShoot()

@event.mesh_message('gameover')
def on_mesh_message():
    mbuild.led_panel.show_image("103c3e3e3e3e3c10103c3e3e3e3e3c10", index = 1)

#       FUNCTIONAL FUNCTIONS
##########################################################################################

# Function to turn a hexa char to decimal
def turnDecimal(char):
    if (char == 'a'):
        return 10
    if (char == 'b'):
        return 11
    if (char == 'c'):
        return 12
    if (char == 'd'):
        return 13
    if (char == 'e'):
        return 14
    if (char == 'f'):
        return 15
    return char

# Function to turn a decimal to a hexa char
def turnHexaDecimal(number):
    if number < 10:
        return number
    if (number == 10):
        return 'a'
    if (number == 11):
        return 'b'
    if (number == 12):
        return 'c'
    if (number == 13):
        return 'd'
    if (number == 14):
        return 'e'
    if (number == 15):
        return 'f'

# Function to check if the shoot hitted and check for gameoverstate
def checkShoot():
    global playerShootX, playerShootY, cursorActive, myShips
    if ((playerShootX, playerShootY) in myShips):
        myShips.remove((playerShootX, playerShootY))
        refreshBackground()
        if len(myShips) == 0:
            mbuild.led_panel.show_image("0000363e1c3e360000363e1c3e360000", index = 1)
            halo.mesh.broadcast('gameover')
            return
    cursorActive = True
    startShoot()