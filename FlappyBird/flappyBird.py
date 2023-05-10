from itertools import cycle
import random
import sys
import pygame
from pygame.locals import *

FPS = 30  # изменять низя
SCREENWIDTH = 288
SCREENHEIGHT = 512
HOLESIZE = 100  # дырка
BASEY = SCREENHEIGHT * 0.79

NUMBERS, SOUNDS, HITMASKS = {}, {}, {}

# списочек из птичек
PLAYERS_LIST = (
    # красная
    (
        'assets/sprites/redbird-upflap.png',
        'assets/sprites/redbird-midflap.png',
        'assets/sprites/redbird-downflap.png',
    ),
    # синяя
    (
        'assets/sprites/bluebird-upflap.png',
        'assets/sprites/bluebird-midflap.png',
        'assets/sprites/bluebird-downflap.png',
    ),
    # желтая
    (
        'assets/sprites/yellowbird-upflap.png',
        'assets/sprites/yellowbird-midflap.png',
        'assets/sprites/yellowbird-downflap.png',
    ),
)

# фон
BACKGROUNDS_LIST = (
    'assets/sprites/background-day.png',
    'assets/sprites/background-night.png',
)

# трубы разных цветов
PIPES_LIST = (
    'assets/sprites/pipe-green.png',
    'assets/sprites/pipe-red.png',
    'assets/sprites/pipe-brown.png',
    'assets/sprites/pipe-pink.png',
    'assets/sprites/pipe-purple.png',
)


try:
    xrange
except NameError:
    xrange = range


class CommonData:
    def __init__(self):
        self.FPSCLOCK = pygame.time.Clock()
        self.SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))


data = CommonData()


def main():

    pygame.init()

    pygame.display.set_caption('Flappy Bird')

    # наши циферки в массивчик переводим
    NUMBERS['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha()
    )

    # wasted
    NUMBERS['gameover'] = pygame.image.load(
        'assets/sprites/gameover.png').convert_alpha()
    # начальный экран
    NUMBERS['message'] = pygame.image.load(
        'assets/sprites/message1.png').convert_alpha()
    # земля
    NUMBERS['base'] = pygame.image.load(
        'assets/sprites/base2.png').convert_alpha()

    # звук
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    SOUNDS['die'] = pygame.mixer.Sound('assets/audio/die' + soundExt)
    SOUNDS['hit'] = pygame.mixer.Sound('assets/audio/hit' + soundExt)
    SOUNDS['point'] = pygame.mixer.Sound('assets/audio/point' + soundExt)
    SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
    SOUNDS['wing'] = pygame.mixer.Sound('assets/audio/wing' + soundExt)

    while True:
        # рандомный фон
        randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        NUMBERS['background'] = pygame.image.load(
            BACKGROUNDS_LIST[randBg]).convert()

        # рандомный птиц
        randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        NUMBERS['player'] = (
            pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )

        # рандомный труб
        pipeindex = random.randint(0, len(PIPES_LIST) - 1)
        NUMBERS['pipe'] = (
            pygame.transform.flip(
                pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), False, True),
            pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
        )

        # хитмаски на трубы
        HITMASKS['pipe'] = (
            getHitmask(NUMBERS['pipe'][0]),
            getHitmask(NUMBERS['pipe'][1]),
        )

        # хитмаски на игрока
        HITMASKS['player'] = (
            getHitmask(NUMBERS['player'][0]),
            getHitmask(NUMBERS['player'][1]),
            getHitmask(NUMBERS['player'][2]),
        )

        movementInfo = showStartAnimation()
        crashInfo = mainGame(movementInfo)
        showGameOverScreen(crashInfo)


def getHitmask(image):
    """возвращает хитмаску"""
    mask = []
    for x in xrange(image.get_width()):
        mask.append([])
        for y in xrange(image.get_height()):
            mask[x].append(bool(image.get_at((x, y))[3]))
    return mask


def showStartAnimation():
    """начальное окно"""
    # начальное положение
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1])

    loopIter = 0

    playerx = int(SCREENWIDTH * 0.2)
    playery = int((SCREENHEIGHT - NUMBERS['player'][0].get_height()) / 2)

    messagex = int((SCREENWIDTH - NUMBERS['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12)

    basex = 0
    # смещение земли налево
    baseShift = NUMBERS['base'].get_width() - NUMBERS['background'].get_width()

    # верх-вниз делает в начале()
    playerShmVals = {'val': 0, 'dir': 1}

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # задаем дефолтные значения
                SOUNDS['wing'].play()
                return {
                    'playery': playery + playerShmVals['val'],
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }

        # регулируемс игрока и землю
        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerShm(playerShmVals)

        # рисуем спрайты
        data.SCREEN.blit(NUMBERS['background'], (0, 0))
        data.SCREEN.blit(NUMBERS['player'][playerIndex],
                         (playerx, playery + playerShmVals['val']))
        data.SCREEN.blit(NUMBERS['message'], (messagex, messagey))
        data.SCREEN.blit(NUMBERS['base'], (basex, BASEY))

        pygame.display.update()
        data.FPSCLOCK.tick(FPS)


def mainGame(movementInfo):
    score = playerIndex = loopIter = 0
    playerIndexGen = movementInfo['playerIndexGen']
    playerx, playery = int(SCREENWIDTH * 0.2), movementInfo['playery']

    basex = movementInfo['basex']
    baseShift = NUMBERS['base'].get_width() - NUMBERS['background'].get_width()

    # берем верхнюю и нижнюю трубу
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # верхние трубы
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]

    # нижние трубы
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    dt = data.FPSCLOCK.tick(FPS)/1000
    pipeVelX = -128 * dt

    playerVelY = -9   # pскорость при изменении у
    playerMaxVelY = 10   # макс скорость по у
    playerMinVelY = -8   # мин скорость по у
    playerAccY = 1   # ускорение вниз
    playerRot = 45   # вращение птички
    playerVelRot = 3   # угл. скорость
    playerRotThr = 20   # порог вращения
    playerFlapAcc = -9   # при взмахе скорость
    playerFlapped = False  # true при взмахе

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > -2 * NUMBERS['player'][0].get_height():
                    playerVelY = playerFlapAcc
                    playerFlapped = True
                    SOUNDS['wing'].play()

        # check for crash here
        crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex},
                               upperPipes, lowerPipes)
        if crashTest[0]:
            return {
                'y': playery,
                'groundCrash': crashTest[1],
                'basex': basex,
                'upperPipes': upperPipes,
                'lowerPipes': lowerPipes,
                'score': score,
                'playerVelY': playerVelY,
                'playerRot': playerRot
            }

        # проверка результата
        playerMidPos = playerx + NUMBERS['player'][0].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + NUMBERS['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                SOUNDS['point'].play()

        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # вращение птички
        if playerRot > -90:
            playerRot -= playerVelRot

        # движение птички
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False

            playerRot = 45

        playerHeight = NUMBERS['player'][playerIndex].get_height()
        playery += min(playerVelY, BASEY - playery - playerHeight)

        # трубы движ налево
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX

        # добавить трубу как только левачя коснется экрана
        if 3 > len(upperPipes) > 0 and 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # убираем первую трубу если видна на нач.экране
        if len(upperPipes) > 0 and upperPipes[0]['x'] < -NUMBERS['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        data.SCREEN.blit(NUMBERS['background'], (0, 0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            data.SCREEN.blit(NUMBERS['pipe'][0], (uPipe['x'], uPipe['y']))
            data.SCREEN.blit(NUMBERS['pipe'][1], (lPipe['x'], lPipe['y']))

        data.SCREEN.blit(NUMBERS['base'], (basex, BASEY))

        showScore(score)

        visibleRot = playerRotThr
        if playerRot <= playerRotThr:
            visibleRot = playerRot

        playerSurface = pygame.transform.rotate(
            NUMBERS['player'][playerIndex], visibleRot)
        data.SCREEN.blit(playerSurface, (playerx, playery))

        pygame.display.update()
        data.FPSCLOCK.tick(FPS)


def showGameOverScreen(crashInfo):
    """показывает wasted"""
    score = crashInfo['score']
    playerx = SCREENWIDTH * 0.2
    playery = crashInfo['y']
    playerHeight = NUMBERS['player'][0].get_height()
    playerVelY = crashInfo['playerVelY']
    playerAccY = 2
    playerRot = crashInfo['playerRot']
    playerVelRot = 7

    basex = crashInfo['basex']

    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

    # звуки смерти
    SOUNDS['hit'].play()
    if not crashInfo['groundCrash']:
        SOUNDS['die'].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery + playerHeight >= BASEY - 1:
                    return

        # изменение по у
        if playery + playerHeight < BASEY - 1:
            playery += min(playerVelY, BASEY - playery - playerHeight)

        # изменение скорости
        if playerVelY < 15:
            playerVelY += playerAccY

        # переворот
        if not crashInfo['groundCrash']:
            if playerRot > -90:
                playerRot -= playerVelRot

        # потрачено
        data.SCREEN.blit(NUMBERS['background'], (0, 0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            data.SCREEN.blit(NUMBERS['pipe'][0], (uPipe['x'], uPipe['y']))
            data.SCREEN.blit(NUMBERS['pipe'][1], (lPipe['x'], lPipe['y']))

        data.SCREEN.blit(NUMBERS['base'], (basex, BASEY))
        showScore(score)

        playerSurface = pygame.transform.rotate(
            NUMBERS['player'][1], playerRot)
        data.SCREEN.blit(playerSurface, (playerx, playery))
        data.SCREEN.blit(NUMBERS['gameover'], (50, 180))

        data.FPSCLOCK.tick(FPS)
        pygame.display.update()


def playerShm(playerShm):

    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
        playerShm['val'] += 1
    else:
        playerShm['val'] -= 1


def getRandomPipe():
    """возврат случайной трубы"""

    gapY = random.randrange(0, int(BASEY * 0.6 - HOLESIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = NUMBERS['pipe'][0].get_height()
    pipeX = SCREENWIDTH + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # верх
        {'x': pipeX, 'y': gapY + HOLESIZE},  # низ
    ]


def showScore(score):
    """вывод счета"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0  #

    for digit in scoreDigits:
        totalWidth += NUMBERS['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        data.SCREEN.blit(NUMBERS['numbers'][digit],
                         (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += NUMBERS['numbers'][digit].get_width()


def checkCrash(player, upperPipes, lowerPipes):
    """вернет тру если столкнется с землей и трубами"""
    pi = player['index']
    player['w'] = NUMBERS['player'][0].get_width()
    player['h'] = NUMBERS['player'][0].get_height()

    # если в зеилю упали
    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    else:

        playerRect = pygame.Rect(player['x'], player['y'],
                                 player['w'], player['h'])
        pipeW = NUMBERS['pipe'][0].get_width()
        pipeH = NUMBERS['pipe'][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):

            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            # если в трубу ударился
            uCollide = pixelCollision(
                playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(
                playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]


def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """проверяем """
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y

    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False


if __name__ == '__main__':
    main()
