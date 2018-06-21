# Owner: Andrew Wang
# Modification to the Dodger program

import pygame, random, sys
from pygame.locals import *
import json
import os

TEXTCOLOR = (255, 255, 255)
BACKGROUNDCOLOR = (0, 0, 0)
NAMEBOXCOLOR = (0, 191, 255)
FPS = 40
BADDIEMINSIZE = 10
BADDIEMAXSIZE = 40
BADDIEMINSPEED = 1
BADDIEMAXSPEED = 8
ADDNEWBADDIERATE = 6
PLAYERMOVERATE = 5

def terminate():
    pygame.quit()
    sys.exit()

def waitForPlayerToPressKey():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: # pressing escape quits
                    terminate()
                if event.key == ord('v'):
                    return 'view'
                if event.key == ord('r'):
                    return 'reset'
                return  

def selectMode():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                if event.key == ord('i'):
                    return 'instructions'
                if event.key == ord('s'):
                    return 'survivalMode'
                if event.key == ord('c'):
                    return 'casualMode'

def selectDifficulty():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: 
                    terminate()
                if event.key == ord('e'):
                    return 'easy'
                if event.key == ord('h'):
                    return 'hard'

def playerHasHitBaddie(playerRect, baddies):
    for b in baddies:
        if playerRect.colliderect(b['rect']):
            return True
    return False

def drawText(text, font, surface, x, y):
    textobj = font.render(text, 1, TEXTCOLOR)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# set up pygame, the window, and the mouse cursor
pygame.init()
mainClock = pygame.time.Clock()
infoObject = pygame.display.Info()
WINDOWWIDTH = infoObject.current_w
WINDOWHEIGHT = infoObject.current_h
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Dodger')
pygame.mouse.set_visible(False)

# set up fonts
font = pygame.font.SysFont(None, 48)

# set up sounds
gameOverSound = pygame.mixer.Sound('gameover.wav')
cheatsActiveSound = pygame.mixer.Sound('cheats.wav')
pointTriplingSound = pygame.mixer.Sound('pickup.wav')
cheatEarnedSound = pygame.mixer.Sound('cheatEarned.wav')

# set up images
playerImage = pygame.image.load('player.png')
playerRect = playerImage.get_rect()
baddieImage = pygame.image.load('baddie.png')

# creates text files for data
filename = 'AWDodgerTopScores.json'

try:
    with open(filename, 'r') as f_obj:
        topScores = json.load(f_obj)
except FileNotFoundError:
    topScores = [0, 0]
topSurvivalScore = int(topScores[0])
topCasualScore = int(topScores[1])

musicPlaying = True

while True:
    # set up variables for later manipulation
    baddieMinSize = BADDIEMINSIZE
    baddieMaxSize = BADDIEMAXSIZE
    baddieMinSpeed = BADDIEMINSPEED
    baddieMaxSpeed = BADDIEMAXSPEED
    addNewBaddieRate = ADDNEWBADDIERATE
    
    pygame.mixer.music.load('opening.mid')
    pygame.mixer.music.play(-1, 0.0)
    
    # set up game mode
    survivalMode = False
    casualMode = False

    mode = ''
    while mode != 'survivalMode' and mode != 'casualMode':
        # show the "Start" screen
        windowSurface.fill(BACKGROUNDCOLOR)
        drawText('Top Survival Score: %s' % (topSurvivalScore), font, windowSurface, 10, 40)
        drawText('Top Casual Score: %s' % (topCasualScore), font, windowSurface, 10, 80)
        drawText('Dodger', font, windowSurface, (WINDOWWIDTH / 2.25), (WINDOWHEIGHT / 3))
        drawText('Press "s" for survival mode', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3) + 50)
        drawText('Press "c" for casual mode', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3) + 100)
        drawText('Press "i" for instructions', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3) + 150)
        pygame.display.update()
        mode = selectMode()
        if mode == 'instructions':
            windowSurface.fill(BACKGROUNDCOLOR)
            drawText('Press any key to continue', font, windowSurface, (WINDOWWIDTH / 3), 20)
            filename_i = 'AWDodgerInstructions.txt'
            try:
                with open(filename_i, 'r') as f_obj:
                    lines = f_obj.readlines()
                for i in range(len(lines)):
                    line = lines[i].rstrip()
                    drawText('%s' % (line), font, windowSurface, (WINDOWWIDTH / 5), 100 + 40 * i)
            except FileNotFoundError:
                drawText('Instructions are currently not available', font, windowSurface, (WINDOWWIDTH / 3.5), (WINDOWHEIGHT / 3) + 100)
            pygame.display.update()
            waitForPlayerToPressKey()

    # clear screen to avoid overlapping text
    windowSurface.fill(BACKGROUNDCOLOR)
    drawText('Top Survival Score: %s' % (topSurvivalScore), font, windowSurface, 10, 40)
    drawText('Top Casual Score: %s' % (topCasualScore), font, windowSurface, 10, 80)

    if mode == 'survivalMode':
        survivalMode = True

    # show difficulty selection in "casual" mode
    elif mode == 'casualMode':
        casualMode = True
        easy = False
        hard = False
        drawText('Press "e" for easy difficulty', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3) + 50)
        drawText('Press "h" for hard difficulty', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3) + 100)
        pygame.display.update()
        difficulty = selectDifficulty()
        if difficulty == 'easy':
            easy = True
        else:
            hard = True

    # set up the start of the game
    baddies = []
    cheats = []
    cheatTimer = 0
    score = 0
    if casualMode and easy:
        lives = 3
    elif casualMode and hard:
        lives = 2
    else:
        lives = 1
    playerRect.topleft = (WINDOWWIDTH / 2, WINDOWHEIGHT - 50)
    moveLeft = moveRight = moveUp = moveDown = False
    reverseCheat = slowCheat = invincibleCheat = triplePointCheat = False
    hitTriggered = False
    baddieAddCounter = 0

    roundedBaddieMinSize = baddieMinSize
    roundedBaddieMinSize = baddieMinSize
    roundedBaddieMaxSize = baddieMaxSize
    roundedBaddieMinSpeed = baddieMinSpeed
    roundedBaddieMaxSpeed = baddieMaxSpeed
    roundedAddNewBaddieRate = addNewBaddieRate
    usedMouse = False

    pygame.mixer.music.load('background.mid')
    if musicPlaying:
        pygame.mixer.music.play(-1, 0.0)
    while True: # the game loop runs while the game part is playing
        # For survival mode, increase difficulty at intervals of 500 points
        if survivalMode:
            if score > 0 and score % 500 == 0:
                if int(baddieMaxSize * 1.2) <= 250:
                    baddieMinSize *= 1.2
                    baddieMaxSize *= 1.2
                    roundedBaddieMinSize = int(baddieMinSize)
                    roundedBaddieMaxSize = int(baddieMaxSize)
                if int(baddieMaxSpeed * 1.2) <= 25:
                    baddieMinSpeed *= 1.2
                    baddieMaxSpeed *= 1.2
                    roundedBaddieMinSpeed = int(baddieMinSpeed)
                    roundedBaddieMaxSpeed = int(baddieMaxSpeed)
                if int(addNewBaddieRate / 1.2) >= 1:
                    addNewBaddieRate /= 1.2
                    roundedAddNewBaddieRate = int(addNewBaddieRate)
            if score > 0 and score % 1000 == 0:
                cheat = random.randint(1, 4)
                cheats.append(cheat)
                cheatEarnedSound.play()
                
        elif casualMode and hard:
            baddieMinSize = 10
            baddieMaxSize = 80
            baddieMinSpeed = 1
            baddieMaxSpeed = 12
            addNewBaddieRate = 3
        
        if triplePointCheat:
            score += 3
        elif casualMode and hard:
            score += 2
        else:
            score += 1

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == MOUSEBUTTONDOWN:
                if survivalMode:
                    if event.button == 1 and len(cheats) >= 1:
                        cheatNum = cheats[0]
                        cheats.remove(cheats[0])
                        if cheatNum == 1:
                            reverseCheat = True
                        elif cheatNum == 2:
                            slowCheat = True
                        elif cheatNum == 3:
                            invincibleCheat = True
                        else:
                            triplePointCheat = True
                        start_ticks = pygame.time.get_ticks()
                elif casualMode:
                    if event.button == 1:
                        reverseCheat = True
                    if event.button == 2:
                        slowCheat = True
                    if event.button == 3:
                        invincibleCheat = True
                        
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                if survivalMode:
                    if event.key == ord('c') and len(cheats) >= 1:
                        cheatNum = cheats[0]
                        cheats.remove(cheats[0])
                        if cheatNum == 1:
                            reverseCheat = True
                        elif cheatNum == 2:
                            slowCheat = True
                        elif cheatNum == 3:
                            invincibleCheat = True
                        else:
                            triplePointCheat = True
                        start_ticks = pygame.time.get_ticks()
                elif casualMode:
                    if event.key == ord('z'):
                        reverseCheat = True
                    if event.key == ord('x'):
                        slowCheat = True
                    if event.key == ord('v'):
                        invincibleCheat = True
                if event.key == K_LEFT or event.key == ord('a'):
                    moveRight = False
                    moveLeft = True
                if event.key == K_RIGHT or event.key == ord('d'):
                    moveLeft = False
                    moveRight = True
                if event.key == K_UP or event.key == ord('w'):
                    moveDown = False
                    moveUp = True
                if event.key == K_DOWN or event.key == ord('s'):
                    moveUp = False
                    moveDown = True

            if event.type == MOUSEBUTTONUP:
                if casualMode:
                    if event.button == 1:
                        reverseCheat = False
                        score = 0
                    if event.button == 2:
                        slowCheat = False
                        score = 0
                    if event.button == 3:
                        invincibleCheat = False
                        score = 0

            if event.type == KEYUP:
                if casualMode:
                    if event.key == ord('z'):
                        reverseCheat = False
                        score = 0
                    if event.key == ord('x'):
                        slowCheat = False
                        score = 0
                    if event.key == ord('v'):
                        invincibleCheat = False
                        score = 0
                if event.key == K_ESCAPE:
                    terminate()
                if event.key == K_LEFT or event.key == ord('a'):
                    moveLeft = False
                if event.key == K_RIGHT or event.key == ord('d'):
                    moveRight = False
                if event.key == K_UP or event.key == ord('w'):
                    moveUp = False
                if event.key == K_DOWN or event.key == ord('s'):
                    moveDown = False
                if event.key == ord('m'):
                    if musicPlaying:
                        pygame.mixer.music.stop()
                    else:
                        pygame.mixer.music.play(-1, 0.0)
                    musicPlaying = not musicPlaying

            if event.type == MOUSEMOTION:
                # If the mouse moves, move the player where the cursor is.
                playerRect.move_ip(event.pos[0] - playerRect.centerx, event.pos[1] - playerRect.centery)

        # Add new baddies at the top of the screen, if needed.
        if not reverseCheat and not slowCheat and not invincibleCheat and not triplePointCheat:
            baddieAddCounter += 1
        if survivalMode and baddieAddCounter >= roundedAddNewBaddieRate:
            baddieAddCounter = 0
            baddieSize = random.randint(roundedBaddieMinSize, roundedBaddieMaxSize)
            newBaddie = {'rect': pygame.Rect(random.randint(0, WINDOWWIDTH-baddieSize), 0 - baddieSize, baddieSize, baddieSize),
                        'speed': random.randint(roundedBaddieMinSpeed, roundedBaddieMaxSpeed),
                        'surface':pygame.transform.scale(baddieImage, (baddieSize, baddieSize)),
                        }

            baddies.append(newBaddie)
        elif casualMode and baddieAddCounter == addNewBaddieRate:
            baddieAddCounter = 0
            baddieSize = random.randint(baddieMinSize, baddieMaxSize)
            newBaddie = {'rect': pygame.Rect(random.randint(0, WINDOWWIDTH-baddieSize), 0 - baddieSize, baddieSize, baddieSize),
                        'speed': random.randint(baddieMinSpeed, baddieMaxSpeed),
                        'surface':pygame.transform.scale(baddieImage, (baddieSize, baddieSize)),
                        }

            baddies.append(newBaddie)

        # Move the player around.
        if moveLeft:
            if playerRect.left <= 0:
                playerRect.right = WINDOWWIDTH
            playerRect.move_ip(-1 * PLAYERMOVERATE, 0)
        if moveRight:
            if playerRect.right >= WINDOWWIDTH:
                playerRect.left = 0
            playerRect.move_ip(PLAYERMOVERATE, 0)
        if moveUp and playerRect.top > 0:
            playerRect.move_ip(0, -1 * PLAYERMOVERATE)
        if moveDown and playerRect.bottom < WINDOWHEIGHT:
            playerRect.move_ip(0, PLAYERMOVERATE)

        # Move the mouse cursor to match the player.
        pygame.mouse.set_pos(playerRect.centerx, playerRect.centery)

        # Move the baddies down.
        for b in baddies:
            if not reverseCheat and not slowCheat:
                b['rect'].move_ip(0, b['speed'])
            elif reverseCheat:
                b['rect'].move_ip(0, -3)
            elif slowCheat:
                b['rect'].move_ip(0, 1)

         # Delete baddies that have fallen past the bottom.
        for b in baddies[:]:
            if b['rect'].top > WINDOWHEIGHT:
                baddies.remove(b)
        
        # Draw the game world on the window.
        windowSurface.fill(BACKGROUNDCOLOR)

        # Draw the score and top score.
        drawText('Score: %s' % (score), font, windowSurface, 10, 0)
        drawText('Top Survival Score: %s' % (topSurvivalScore), font, windowSurface, 10, 40)
        drawText('Top Casual Score: %s' % (topCasualScore), font, windowSurface, 10, 80)
        drawText('Lives: %s' % (lives), font, windowSurface, 10, 120)
        drawText('Cheat Timer: %s' % (cheatTimer), font, windowSurface, 10, 160)

        # Draw the player's rectangle
        windowSurface.blit(playerImage, playerRect)

        # Draw each baddie
        for b in baddies:
            windowSurface.blit(b['surface'], b['rect'])

        pygame.display.update()

        # Check if any of the baddies have hit the player.
        if playerHasHitBaddie(playerRect, baddies):
            if invincibleCheat:
                pass
            elif not invincibleCheat and lives > 1:
                lives -= 1
                invincibleCheat = True
                hitTriggered = True
                start_ticks = pygame.time.get_ticks()
            elif lives == 1: # game over condition
                lives -= 1
                if survivalMode and score > topSurvivalScore:
                    topSurvivalScore = score # set new top score for survival mode
                elif casualMode and score > topCasualScore:
                    topCasualScore = score # set new top score for casual mode
                topScores = [topSurvivalScore, topCasualScore]
                with open(filename, 'w') as f_obj:
                    json.dump(topScores, f_obj)

                # Update game world
                windowSurface.fill(BACKGROUNDCOLOR)
                drawText('Score: %s' % (score), font, windowSurface, 10, 0)
                drawText('Top Survival Score: %s' % (topSurvivalScore), font, windowSurface, 10, 40)
                drawText('Top Casual Score: %s' % (topCasualScore), font, windowSurface, 10, 80)
                drawText('Lives: %s' % (lives), font, windowSurface, 10, 120)
                windowSurface.blit(playerImage, playerRect)
                for b in baddies:
                    windowSurface.blit(b['surface'], b['rect'])
                pygame.display.update()
                break
        # Respond to when the invincibility mode is activated in casual mode
        if invincibleCheat and hitTriggered:
            pygame.mixer.music.stop()
            cheatsActiveSound.play()
            seconds = (pygame.time.get_ticks() - start_ticks)/1000
            cheatTimer = int(3 - seconds)
            if cheatTimer <= 0:
                cheatsActiveSound.stop()
                invincibleCheat = False
                hitTriggered = False
                if musicPlaying:
                    pygame.mixer.music.play(-1, 0.0)
                cheatTimer = 0

        # Respond to when a cheat is activated in survival mode
        if survivalMode and (reverseCheat or slowCheat or invincibleCheat or triplePointCheat):
            if not triplePointCheat:
                pygame.mixer.music.stop()
                cheatsActiveSound.play()
                maxTime = 10
            else:
                pointTriplingSound.play()
                maxTime = 7
            seconds = (pygame.time.get_ticks() - start_ticks)/1000
            cheatTimer = int(maxTime - seconds)
            if not triplePointCheat and cheatTimer <= 0:
                cheatsActiveSound.stop()
                reverseCheat = False
                slowCheat = False
                invincibleCheat = False
                if musicPlaying:
                    pygame.mixer.music.play(-1, 0.0)
                cheatTimer = 0
            elif triplePointCheat and cheatTimer <= 0:
                pointTriplingSound.stop()
                triplePointCheat = False
                cheatTimer = 0
        mainClock.tick(FPS)

    # Stop the game and show the "Game Over" screen.
    pygame.mixer.music.stop()
    gameOverSound.play()

    # Have player enter name.
    nameBox1 = pygame.Rect(WINDOWWIDTH/3, WINDOWHEIGHT/2.75, WINDOWWIDTH/2.8, WINDOWHEIGHT/9)
    nameBox2 = pygame.Rect(WINDOWWIDTH/3 + 3, WINDOWHEIGHT/2.75 + 3, WINDOWWIDTH/2.8 - 6, WINDOWHEIGHT/9 - 6)
    name = ''
    done = False
    while not done: # Allows player to enter characters until enter key is pressed.
        pygame.draw.rect(windowSurface, NAMEBOXCOLOR, nameBox1, 3)
        pygame.draw.rect(windowSurface, BACKGROUNDCOLOR, nameBox2, 0)
        drawText('Please enter your name:', font, windowSurface, nameBox2.x, nameBox2.y)
        drawText(name, font, windowSurface, nameBox2.x, nameBox2.y + 40)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_RETURN:
                    done = True
                elif event.key == K_BACKSPACE:
                    name = name[:-1]
                elif len(name) <= 25:
                    name += event.unicode

    if survivalMode:
        filename_2 = 'AWDodgerSurvivalScoreBoard.json'
    else:
        filename_2 = 'AWDodgerCasualScoreBoard.json'
    try:
        with open(filename_2, 'r') as f_obj:
            scoreBoard = json.load(f_obj)
    except FileNotFoundError:
        scoreBoard = []
    scoreBoard.append([name, score])
    scoreBoard.sort(key=lambda x:x[1], reverse=True)
    with open(filename_2, 'w') as f_obj:
        json.dump(scoreBoard, f_obj)

    while True: # Game over screen
        windowSurface.fill(BACKGROUNDCOLOR)
        drawText('Score: %s' % (score), font, windowSurface, 10, 0)
        drawText('Top Survival Score: %s' % (topSurvivalScore), font, windowSurface, 10, 40)
        drawText('Top Casual Score: %s' % (topCasualScore), font, windowSurface, 10, 80)
        drawText('Lives: %s' % (lives), font, windowSurface, 10, 120)
        drawText('GAME OVER', font, windowSurface, (WINDOWWIDTH / 2.25), (WINDOWHEIGHT / 3))
        drawText('Press a key to play again', font, windowSurface, (WINDOWWIDTH / 2.85), (WINDOWHEIGHT / 3) + 50)
        drawText('Press "v" to view score board', font, windowSurface, (WINDOWWIDTH / 2.85), (WINDOWHEIGHT / 3) + 100)
        drawText('Press "r" to reset all scores', font, windowSurface, (WINDOWWIDTH / 2.85), (WINDOWHEIGHT / 3) + 150)
        pygame.display.update()
        state = waitForPlayerToPressKey()
        if state == 'view': # Allows player to view scoreboard
            windowSurface.fill(BACKGROUNDCOLOR)
            drawText('Score: %s' % (score), font, windowSurface, 10, 0)
            drawText('Top Survival Score: %s' % (topSurvivalScore), font, windowSurface, 10, 40)
            drawText('Top Casual Score: %s' % (topCasualScore), font, windowSurface, 10, 80)
            drawText('Lives: %s' % (lives), font, windowSurface, 10, 120)
            drawText('Press "s" for survival mode scores', font, windowSurface, (WINDOWWIDTH / 2.85), (WINDOWHEIGHT / 3))
            drawText('Press "c" for casual mode scores', font, windowSurface, (WINDOWWIDTH / 2.85), (WINDOWHEIGHT / 3) + 50)
            pygame.display.update()
            mode = selectMode()
            if mode == 'survivalMode':
                header = 'Survival'
                filename_2 = 'AWDodgerSurvivalScoreBoard.json'
            else:
                header = 'Casual'
                filename_2 = 'AWDodgerCasualScoreBoard.json'
            try:
                with open(filename_2, 'r') as f_obj:
                    scoreBoard = json.load(f_obj)
            except FileNotFoundError:
                windowSurface.fill(BACKGROUNDCOLOR)
                drawText('Score: %s' % (score), font, windowSurface, 10, 0)
                drawText('Top Survival Score: %s' % (topSurvivalScore), font, windowSurface, 10, 40)
                drawText('Top Casual Score: %s' % (topCasualScore), font, windowSurface, 10, 80)
                drawText('Lives: %s' % (lives), font, windowSurface, 10, 120)
                drawText('No Scores For %s Mode' % (header), font, windowSurface, (WINDOWWIDTH / 2.85), (WINDOWHEIGHT / 3))
            else:
                windowSurface.fill(BACKGROUNDCOLOR)
                drawText('Scoreboard For %s Mode' % (header), font, windowSurface, 10, 0)
                scoreBoardLength = min(10, len(scoreBoard))
                for i in range(scoreBoardLength):
                    drawText('%s: %s' % (scoreBoard[i][0], scoreBoard[i][1]), font, windowSurface, 10, 40 + 40 * i)
            drawText('Press a key to return to previous menu', font, windowSurface, 10, 600)
            pygame.display.update()
            waitForPlayerToPressKey()
        elif state == 'reset': # Gives player option to reset all scores
            windowSurface.fill(BACKGROUNDCOLOR)
            drawText('Score: %s' % (score), font, windowSurface, 10, 0)
            drawText('Top Survival Score: %s' % (topSurvivalScore), font, windowSurface, 10, 40)
            drawText('Top Casual Score: %s' % (topCasualScore), font, windowSurface, 10, 80)
            drawText('Lives: %s' % (lives), font, windowSurface, 10, 120)
            drawText('Are you sure that you want to reset all scores? (Press "r" to reset)', font, windowSurface, (WINDOWWIDTH / 7.5), (WINDOWHEIGHT / 3))
            pygame.display.update()
            state = waitForPlayerToPressKey()
            if state == 'reset':
                score = 0
                topSurvivalScore = 0
                topCasualScore = 0
                try:
                    os.remove('AWDodgerTopScores.json')
                except FileNotFoundError:
                    pass
                try:
                    os.remove('AWDodgerSurvivalScoreBoard.json')
                except FileNotFoundError:
                    pass
                try:
                    os.remove('AWDodgerCasualScoreBoard.json')
                except FileNotFoundError:
                    pass
                windowSurface.fill(BACKGROUNDCOLOR)
                drawText('Score: %s' % (score), font, windowSurface, 10, 0)
                drawText('Top Survival Score: %s' % (topSurvivalScore), font, windowSurface, 10, 40)
                drawText('Top Casual Score: %s' % (topCasualScore), font, windowSurface, 10, 80)
                drawText('Lives: %s' % (lives), font, windowSurface, 10, 120)
                drawText('All scores cleared!', font, windowSurface, (WINDOWWIDTH / 2.5), (WINDOWHEIGHT / 3))
                drawText('Press a key to return to previous menu', font, windowSurface, 10, 600)
                pygame.display.update()
                waitForPlayerToPressKey()
            else:
                pass
        else:
            break

    gameOverSound.stop()
    windowSurface.fill(BACKGROUNDCOLOR)
