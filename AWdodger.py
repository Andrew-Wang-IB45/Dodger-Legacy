# Owner: Andrew Wang
# Modification to the Dodger program

import pygame, random, sys
from pygame.locals import *

TEXTCOLOR = (255, 255, 255)
BACKGROUNDCOLOR = (0, 0, 0)
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
                return

def selectMode():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
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
cheatEarnedSound = pygame.mixer.Sound('cheatEarned.wav')

# set up images
playerImage = pygame.image.load('player.png')
playerRect = playerImage.get_rect()
baddieImage = pygame.image.load('baddie.png')

topSurvivalScore = 0
topCasualScore = 0

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

    # show the "Start" screen
    drawText('Top Survival Score: %s' % (topSurvivalScore), font, windowSurface, 10, 40)
    drawText('Top Casual Score: %s' % (topCasualScore), font, windowSurface, 10, 80)
    drawText('Dodger', font, windowSurface, (WINDOWWIDTH / 2.25), (WINDOWHEIGHT / 3))
    drawText('Press "s" for survival mode', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3) + 50)
    drawText('Press "c" for casual mode', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3) + 100)
    pygame.display.update()
    mode = selectMode()

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

    pygame.mixer.music.load('background.mid')
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
                start_ticks = pygame.time.get_ticks()
                
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

            if event.type == KEYDOWN:
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

            if event.type == MOUSEMOTION:
                # If the mouse moves, move the player where the cursor is.
                playerRect.move_ip(event.pos[0] - playerRect.centerx, event.pos[1] - playerRect.centery)

        # Add new baddies at the top of the screen, if needed.
        if not reverseCheat and not slowCheat:
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
        if moveLeft and playerRect.left > 0:
            playerRect.move_ip(-1 * PLAYERMOVERATE, 0)
        if moveRight and playerRect.right < WINDOWWIDTH:
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
                b['rect'].move_ip(0, -2)
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
            elif lives == 1:
                if survivalMode and score > topSurvivalScore:
                    topSurvivalScore = score # set new top score for survival mode
                elif casualMode and score > topCasualScore:
                    topCasualScore = score # set new top score for casual mode
                break

        if invincibleCheat and hitTriggered:
            pygame.mixer.music.stop()
            cheatsActiveSound.play()
            seconds = (pygame.time.get_ticks() - start_ticks)/1000
            if seconds >= 3:
                cheatsActiveSound.stop()
                invincibleCheat = False
                hitTriggered = False
                pygame.mixer.music.play(-1, 0.0)
        if survivalMode and (reverseCheat or slowCheat or invincibleCheat or triplePointCheat):
            pygame.mixer.music.stop()
            cheatsActiveSound.play()
            seconds = (pygame.time.get_ticks() - start_ticks)/1000
            if seconds >= 7:
                cheatsActiveSound.stop()
                reverseCheat = False
                slowCheat = False
                invincibleCheat = False
                triplePointCheat = False
                pygame.mixer.music.play(-1, 0.0)
        mainClock.tick(FPS)

    # Stop the game and show the "Game Over" screen.
    pygame.mixer.music.stop()
    gameOverSound.play()

    drawText('GAME OVER', font, windowSurface, (WINDOWWIDTH / 2.25), (WINDOWHEIGHT / 3))
    drawText('Press a key to play again', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3) + 50)
    pygame.display.update()
    
    waitForPlayerToPressKey()

    gameOverSound.stop()
    windowSurface.fill(BACKGROUNDCOLOR)