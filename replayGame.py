from math import floor
from os import environ
import sys
import pickle
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # https://stackoverflow.com/questions/51464455/how-to-disable-welcome-message-when-importing-pygame

import pygame

pygame.display.init()
pygame.font.init()
import objects
import functions

def main(fenList, fen = "", whiteTime = 0, blackTime = 0, resume = False):     #main loop
    # print(fenList)
    if not functions.checkFENs(fenList):
        raise Exception("invalid FENs somewhere")
    ## resume from save
    if resume:
        try:
            with open("save.pkl", "rb") as loadedSave:
                fen, aiPlaysWhite, aiPlaysBlack, rotation, passPlay, whiteTime, blackTime, difficulty, fens, pgn = pickle.load(loadedSave)
            loadedSave.close()
        except Exception as e:
            print(f"No save! Starting default game. {e}")
            pass
    ## ------------- Constants ------------------ ##
    clock = pygame.time.Clock()
    pygame.display.set_caption("Chess - Replay")
    halfsize = 800 # set square window resolution
    resolution = (halfsize, halfsize)
    # sideSizeX = resolution[0]*0.09
    # sideSizeY = resolution[1]*0.09

    # squareSizeTuple = (resolution[0]*0.09, resolution[1]*0.09)
    flags= pygame.SCALED
    window = pygame.display.set_mode(size=resolution, flags = flags, vsync = 1)     #creates a window
    DEFAULTFONT = pygame.font.SysFont("Sans", round(resolution[0]*0.02))
    TIMERFONT = pygame.font.SysFont("Sans", round(resolution[0]*0.05))
    boardObject = objects.board('board.png', False, window, resolution, rotation = True)     # creates the board
    bitboardsObject = objects.Bitboards(fenList[0]) # sets the initial position to be 0
    pieces = functions.loadPieces(boardObject, bitboardsObject, window, True) # loads in pieces.
    bg = pygame.transform.scale(pygame.image.load("bg" + str(int(1)) + ".png").convert(), resolution)
    bgrect = bg.get_rect()
    blackClock = None
    whiteClock = None
    # fen = bitboardsObject.getFEN()
    bitboardsObject.fenList = fenList
    if blackTime > 0 or whiteTime > 0:
        staleMate, checkMate, reason = functions.checkEnd(bitboardsObject, pieces, blackClock, whiteClock)
    else:
        staleMate, checkMate, reason = functions.checkEnd(bitboardsObject, pieces)


    # back and forward buttons
    buttonGroup = pygame.sprite.Group()
    backButton = objects.stepButton(bitboardsObject, boardObject, window, pieces, operation = -1, resolution = resolution)
    forwardButton = objects.stepButton(bitboardsObject, boardObject, window, pieces, operation = 1, resolution = resolution)
    buttonGroup.add(backButton)
    buttonGroup.add(forwardButton)


    ## ------------------------- Main Loop -------------------------- ##
    while True:
        # pieceCanBeSelected = False
        # pointerPos = functions.absoluteToRelativeCoords(pygame.mouse.get_pos(), boardObject)
        if whiteClock and blackClock:
            whiteMins, whiteSecs =  divmod(whiteClock.t, 60)    # converts seconds to minutes, seconds and less than a second
            blackMins, blackSecs =  divmod(blackClock.t, 60)
            whiteSecsStr = (str(floor(whiteSecs)).zfill(2))[0:2]  # gets just the seconds
            whiteMilliStr = str(floor(100*(float(whiteSecs) - float(whiteSecsStr)))).zfill(2)   # gets the milliseconds into a 2 digit string
            blackSecsStr = (str(int(blackSecs)).zfill(2))[0:2]
            blackMilliStr = str(floor(100*(float(blackSecs) - float(blackSecsStr)))).zfill(2)
            whiteClockText = TIMERFONT.render((f"{round(whiteMins)}:{whiteSecsStr}.{whiteMilliStr}"), True, "black").convert_alpha()    # defines the actual strings seen
            blackClockText = TIMERFONT.render((f"{round(blackMins)}:{blackSecsStr}.{blackMilliStr}"), True, "black").convert_alpha()
        if bitboardsObject.getTurn():
            text = DEFAULTFONT.render(str(f"White to play, fps {str(int(clock.get_fps()))} time: {str(clock.get_rawtime())} ply: {bitboardsObject.positionInGame}"), True, "black") .convert_alpha() # shows the debug text
        else:
            text = DEFAULTFONT.render(str(f"Black to play, fps {str(int(clock.get_fps()))} time: {str(clock.get_rawtime())} ply: {bitboardsObject.positionInGame}"), True, "black") .convert_alpha()
        fenText = DEFAULTFONT.render(str(bitboardsObject.getFEN()), True, "black")
        # pgnText = DEFAULTFONT.render(str(bitboardsObject.pgn)[len(bitboardsObject.pgn)-70::], True, "black")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if whiteClock and blackClock:
                    whiteClock.timer.stop() # stops the timers so the program doesn't hang
                    blackClock.timer.stop()
                    whiteClock.kill()   # kills them for the same reason
                    blackClock.kill()
                sys.exit()
                pygame.display.quit()
                pygame.quit()
                raise Exception('Close')    # i really want it to quit at this point if all else fails.

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for stepButton in buttonGroup:
                    currentRect = stepButton.rect
                    if currentRect.collidepoint(pygame.mouse.get_pos()):
                        pieces =stepButton.clicked()

        window.blit(bg, bgrect) # putting background on screen
        window.blit(text, text.get_rect())  # putting debug text on the screen
        window.blit(fenText, pygame.Rect(0, resolution[1]*0.020, resolution[0]*0.100, resolution[1]*0.100)) # putting the fen on the screen
        buttonGroup.draw(window) # draws the forward backwards buttons
        pieces.update()

        boardObject.draw()
        boardObject.update()
        pieces.draw(boardObject.getSurface())
        if whiteClock and blackClock:   # drawing the clock if I get on to it for replay.
            window.blit(whiteClockText, pygame.Rect(resolution[0]*0.730, resolution[1]*0.900, resolution[0]*0.100, resolution[1]*0.100))
            window.blit(blackClockText, pygame.Rect(resolution[0]*0.730, resolution[1]*0.050, resolution[0]*0.100, resolution[1]*0.100))

        pygame.display.update()
        clock.tick()

if __name__ == "__main__":
    replayFile = open("replayFile.txt", "r")
    main(fenList = replayFile.read().splitlines())
