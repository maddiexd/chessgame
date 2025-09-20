from math import floor
from os import environ

import sys
import pickle
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # https://stackoverflow.com/questions/51464455/how-to-disable-welcome-message-when-importing-pygame

import pygame
import bitarray
from threading import Thread

pygame.display.init()
pygame.font.init()
import objects
import functions
reason = False


def main(fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", rotation = True, passPlay = False, perftDepth = -1, aiPlaysBlack = True, aiPlaysWhite = False, whiteTime = 0, blackTime = 0, resume = False, difficulty = 2):     #main loop
    ## resume from save
    if resume:
        try:
            with open("save.pkl", "rb") as loadedSave:
                fen, aiPlaysWhite, aiPlaysBlack, rotation, passPlay, whiteTime, blackTime, difficulty, fens, pgn = pickle.load(loadedSave)
            loadedSave.close()
        except Exception as e:
            print(f"No save! Starting default game. {e}")
            pass
    else:
        pgn = ""
        fens = []
    # print("rotation: ", rotation, "passPlay: ", passPlay, "fen: ", fen)
    ## ------------- Constants ------------------ ##
    clock = pygame.time.Clock()
    pygame.display.set_caption("Chess - Game")
    halfsize = 800 # set square window resolution
    resolution = (halfsize, halfsize)
    # sideSizeX = resolution[0]*0.09
    # sideSizeY = resolution[1]*0.09

    # squareSizeTuple = (resolution[0]*0.09, resolution[1]*0.09)
    flags= pygame.SCALED
    window = pygame.display.set_mode(size=resolution, flags = flags, vsync = 0)     #creates a window
    DEFAULTFONT = pygame.font.SysFont("Sans", round(resolution[0]*0.02))
    TIMERFONT = pygame.font.SysFont("Sans", round(resolution[0]*0.05))
    boardObject = objects.board('board.png', False, window, resolution, rotation = rotation)     # creates the board
    if not fen: # creates the bitboard object from the fen given, if not will start with default, can change later with some actual validation.
        bitboardsObject = objects.Bitboards()
    else:
        bitboardsObject = objects.Bitboards(str(fen))
    bitboardsObject.pgn = pgn
    if passPlay:
        rotation = bitboardsObject.getTurn()    # sets correct rotation
    pieces = functions.loadPieces(boardObject, bitboardsObject, window, rotation) # loads in pieces.
    if passPlay:
        bg = pygame.transform.scale(pygame.image.load("bg" + str(int(bitboardsObject.getTurn() == True)) + ".png").convert(), resolution)   # sets background for rotation
    else:
        bg = pygame.transform.scale(pygame.image.load("bg" + str(int(rotation == True)) + ".png").convert(), resolution)
    bgrect = bg.get_rect()
    if blackTime > 0 or whiteTime > 0:
        blackClock = objects.chessClock(blackTime, bitboardsObject.getTurn()) # initiating clocks
        blackClockThread = Thread(target=lambda: blackClock.startClock())
        blackClockThread.daemon=True
        whiteClock = objects.chessClock(whiteTime, not bitboardsObject.getTurn())
        whiteClockThread = Thread(target=lambda: whiteClock.startClock())
        blackClockThread.daemon=True
        blackClock.refreshClock()   # applies paused status
        whiteClock.refreshClock()
        gameOver = blackClock.end or whiteClock.end
    else:
        gameOver = False
        blackClock = None
        whiteClock = None
    blackTeamObject = objects.Team("Black") # defining the team object, for points
    whiteTeamObject = objects.Team("White")
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR) # set cursor to crosshair because it looks cooler
    # if passPlay:
    #     rotation = bitboardsObject.getTurn()
    #     boardObject.rotate(rotation)
    #     for everyPiece in pieces:
    #         everyPiece.rotate(rotation)
    # pushBoard = bitarray.bitarray(64) # initialise variables for first loop.
    # takingBoard = bitarray.bitarray(64)
    # checkersCount = 0
    # moving = False
    clicked = False
    outlineDraw = False
    piece = None
    thinking = (aiPlaysBlack and not bitboardsObject.getTurn()) or (aiPlaysWhite and bitboardsObject.getTurn())
    # stop = False
    validBoards = bitarray.bitarray(64)
    selectedPiece = None
    # loopCounter=0
    # fens = []
    initialCoord = []
    nextCoord = []
    repetitionList = []
    fen = bitboardsObject.getFEN()

    functions.setStockfishSkill(int(difficulty))
    if blackTime > 0 or whiteTime > 0:
        gameOver, checkMate, reason = functions.checkEnd(bitboardsObject, pieces, blackClock, whiteClock)
    else:
        gameOver, checkMate, reason = functions.checkEnd(bitboardsObject, pieces)
    with open("save.pkl", "wb") as saveFile:
        if blackClock and whiteClock:
            pickle.dump([fen, aiPlaysWhite, aiPlaysBlack, rotation, passPlay, blackClock.t, whiteClock.t, difficulty, fens, bitboardsObject.pgn], file = saveFile)
        else:
            pickle.dump([fen, aiPlaysWhite, aiPlaysBlack, rotation, passPlay, 0, 0, difficulty, fens, bitboardsObject.pgn], file = saveFile)
    saveFile.close()
    fens.append(fen)
    if thinking:    # start and/or declare AI threads
        aiThread = objects.threadThatReturns(target= lambda: functions.getStockfishMove(bitboardsObject, whiteClock, blackClock))
        aiThread.daemon=True
        aiThread.start()
    elif aiPlaysBlack or aiPlaysWhite:
        aiThread = objects.threadThatReturns(target= lambda: functions.getStockfishMove(bitboardsObject, whiteClock, blackClock))
        aiThread.daemon=True
    else:
        aiThread = False
    # print(bitboardsObject.getFEN())
    # file = open("data2.txt", "a")
    if perftDepth >= 0: # do perft if specified
        ##depth = 2
        print("\n" + str(functions.perft(bitboardsObject, pieces, perftDepth, perftDepth)))


    ## ------------------------- Main Loop -------------------------- ##
    while True:
        moved = False
        if blackClock != None and whiteClock != None:
            if not checkMate:
                gameOver = blackClock.end or whiteClock.end
            if gameOver and not reason:
                temp, checkMate, reason = functions.checkEnd(bitboardsObject, pieces, blackClock, whiteClock)
                piece = None
                selectedPiece = None
                validBoards = None
        plyCount = bitboardsObject.getPlyCounter()
        # pieceCanBeSelected = False
        pointerPos = functions.absoluteToRelativeCoords(pygame.mouse.get_pos(), boardObject)
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
            text = DEFAULTFONT.render(str(f"White to play, fps {str(int(clock.get_fps()))} time: {str(clock.get_rawtime())} thinking: {str(thinking)} gameOver: {str(gameOver)} checkmate: {str(checkMate)} difficulty: {difficulty}"), True, "black").convert_alpha() # shows the debug text
        else:
            text = DEFAULTFONT.render(str(f"Black to play, fps {str(int(clock.get_fps()))} time: {str(clock.get_rawtime())} thinking: {str(thinking)} gameOver: {str(gameOver)} checkmate: {str(checkMate)} difficulty: {difficulty}"), True, "black") .convert_alpha()
        fenText = DEFAULTFONT.render(str(fen), True, "black")
        pgnText = DEFAULTFONT.render(str(bitboardsObject.pgn)[len(bitboardsObject.pgn)-70::], True, "black")

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
                # break

                # 0/0
            elif event.type == pygame.MOUSEMOTION:
                if clicked and piece and not bitboardsObject.promotionLock and not thinking and not gameOver:
                    # print("ghost moving")
                    piece.move(pointerPos, bitboardsObject, clicked, pieces, validBoards)   # moves the piece smoothly when dragged
                    pygame.mouse.set_visible(0)
                    outlineDraw = True

            elif event.type == pygame.MOUSEBUTTONUP and not thinking:
                if clicked:
                    clicked = False
                    pygame.mouse.set_visible(1)
                    outlineDraw = False
                    if piece:
                        newCoord = list(functions.boardAbsoluteToBoardCoord(pointerPos))
                        if not rotation:
                            newCoord[1] = 9 - newCoord[1]
                            newCoord[0] = 9 - newCoord[0]
                        newCoord = tuple(newCoord)
                        moved = piece.move(newCoord, bitboardsObject, clicked, pieces, validBoards, blackTeamObject, whiteTeamObject) # snap the piece to the nearest square.
                        if moved and not bitboardsObject.promotionLock:
                            validBoards = bitarray.bitarray(64) # reset things for the next turn
                            selectedPiece = None
                            if passPlay:
                                initialCoord = piece.prevPos
                                nextCoord = piece.getBoardCoords()
                            # print("successful move")
                            # takeCheck(piece, bitboardsObject, blackTeamObject, whiteTeamObject, pieces)
                            # print("drag moved")
                            bitboardsObject.toggleTurn() # switch turn.
                            # for iterPiece in pieces:
                            #     # print("iterpiece", iterPiece.getType())
                            #     if (iterPiece.getType() == 5 and bitboardsObject.getTurn()) or (iterPiece.getType() == 11 and not bitboardsObject.getTurn()):
                            #         kingPiece = iterPiece
                            #         pushBoard, takingBoard, checkersCount = getCheckingPieces(kingPiece, bitboardsObject, pieces)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not thinking and not gameOver:
                if not bitboardsObject.promotionLock:
                    piece = functions.checkForClicked(pieces, boardObject)
                    if piece:
                        if ((piece.getType() <= 5 and bitboardsObject.getTurn()) and not aiPlaysWhite) or ((piece.getType() > 5 and not bitboardsObject.getTurn()) and not aiPlaysBlack):
                            # print("yes piece")
                            outlineDraw = True  # turn on drawing the outlines of the squares for dragging and dropping
                            pass
                        else:
                            pygame.mouse.set_visible(1)
                            outlineDraw = False
                            # print(aiPlaysBlack, aiPlaysWhite)
                            # print("no piece")
                            piece = None
                    if piece:
                        clicked = True
                        # print("clicked")
                        if selectedPiece != piece:
                            piece.move(pointerPos, bitboardsObject, clicked, pieces, validBoards)
                            if (piece.getType() <= 5 and bitboardsObject.getTurn()) or (piece.getType() > 5 and not bitboardsObject.getTurn()):
                                validBoards = functions.getLegal(bitboardsObject, piece, pieces)[0]
                                # gets the valid moves for the selected piece
                                selectedPiece = piece

                    elif selectedPiece:
                        moved= functions.fullClickMove(selectedPiece, pointerPos, pieces, bitboardsObject, validBoards, blackTeamObject, whiteTeamObject, rotation = rotation) # move the piece to the clicked square
                        if moved and not bitboardsObject.promotionLock:
                                if passPlay:
                                    initialCoord = selectedPiece.prevPos
                                    nextCoord = selectedPiece.getBoardCoords()
                                # print("take check")
                                piece = None    # reset things for the next turn again
                                # takeCheck(selectedPiece, bitboardsObject, blackTeamObject, whiteTeamObject, pieces)
                                # print("click moved")
                                bitboardsObject.toggleTurn()
                                # for iterPiece in pieces:
                                #     # print("iterpiece", iterPiece.getType())
                                #     if (iterPiece.getType() == 5 and bitboardsObject.getTurn()) or (iterPiece.getType() == 11 and not bitboardsObject.getTurn()):
                                #         kingPiece = iterPiece
                                #         pushBoard, takingBoard, checkersCount = getCheckingPieces(kingPiece, bitboardsObject, pieces)
                        validBoards = bitarray.bitarray(64)
                        selectedPiece = None
                    else:
                        pass
                else:
                    for promoteButton in promoteGroup:
                        currentRect = promoteButton.rect
                        if currentRect.collidepoint(pygame.mouse.get_pos()):
                            promoteButton.clicked()
                            piece = None

                # print(selectedPiece)
            else:
                continue


        # stockfishMove = getStockfishMove(bitboardsObject)

        if (aiPlaysBlack or aiPlaysWhite) and aiThread and not gameOver:
            if aiThread.is_alive() == False and (bitboardsObject.getTurn() == aiPlaysWhite or bitboardsObject.getTurn() != aiPlaysBlack): # checks for correct turn and if stockfish has finished getting a move
                # print("done")
                # stockfishMove  = aiThread
                stockfishMove = aiThread.result


                if isinstance(stockfishMove, str):
                    initialCoord = functions.standardDecodeCoord(stockfishMove[0:2])
                    nextCoord = functions.standardDecodeCoord(stockfishMove[2:4])
                    if bitboardsObject.getTurn():
                        promotionSelection = functions.getPieceNumber(stockfishMove[4::].upper())
                    else:
                        promotionSelection = functions.getPieceNumber(stockfishMove[4::].lower())
                    # if promotionSelection:
                    #     print(promotionSelection)
                    foundPiece = False
                    for compPiece in pieces:
                        if compPiece.getBoardCoords() == initialCoord:
                            foundPiece = compPiece

                    if foundPiece and not moved:
                        foundPiece.move(nextCoord, bitboardsObject, False, pieces, ~bitarray.bitarray(64), blackTeamObject, whiteTeamObject, promotionSelection)
                        # functions.takeCheck(foundPiece, bitboardsObject, blackTeamObject, whiteTeamObject, pieces)
                        # print("internally moved")
                        bitboardsObject.toggleTurn()

                        piece = None
                        foundPiece = None
                        stockfishMove = None
                        promotionSelection = None

                    else:
                        pass
            if aiThread.is_alive() == False and (bitboardsObject.getTurn() == aiPlaysWhite or bitboardsObject.getTurn() != aiPlaysBlack):
                thinking = True
                aiThread = objects.threadThatReturns(target= lambda: functions.getStockfishMove(bitboardsObject, whiteClock, blackClock))
                aiThread.start()
            elif aiThread.is_alive():
                thinking = True
            else:
                thinking = False

        if validBoards and not clicked and piece and not bitboardsObject.promotionLock and not gameOver:
            functions.renderBitboard(validBoards, boardObject, "#a8d08d", rotation = rotation)

            pass
        # renderBitboard(takingBoard, boardObject, "red", 0.06)
        # renderBitboard(pushBoard, boardObject, "blue", 0.06)
        # try:
        #     renderBitboard((passentPinned[1]), boardObject)
        #     renderBitboard((passentPinned[2]), boardObject, colour="pink", size=0.09)
        # except:
        #     pass
        if plyCount != bitboardsObject.getPlyCounter():
            if blackClock and whiteClock:
                blackClock.paused = bitboardsObject.getTurn()
                blackClock.refreshClock()
                whiteClock.paused = not bitboardsObject.getTurn()
                whiteClock.refreshClock()
            fen = bitboardsObject.getFEN()
            fens.append(fen)
            with open("save.pkl", "wb") as saveFile:
                if blackClock and whiteClock:
                    pickle.dump([fen, aiPlaysWhite, aiPlaysBlack, rotation, passPlay, whiteClock.t, blackClock.t, difficulty, fens, bitboardsObject.pgn], file = saveFile)
                else:
                    pickle.dump([fen, aiPlaysWhite, aiPlaysBlack, rotation, passPlay, 0, 0, difficulty, fens, bitboardsObject.pgn], file = saveFile)
            saveFile.close()
            # print("\n" + str(perft(bitboardsObject, pieces, 3,3, file)))
            # print("----------------------")
            if blackClock and whiteClock:
                gameOver, checkMate, reason = functions.checkEnd(bitboardsObject, pieces, blackClock, whiteClock)
            else:
                gameOver, checkMate, reason = functions.checkEnd(bitboardsObject, pieces)
            spaceCounter = 0
            endPoint = 0
            for i, value in enumerate(fen):    # remove end numbers for repetition rules
                if value == " ":
                    spaceCounter +=1
                    if spaceCounter >= 4 and not endPoint > 0:
                        endPoint = i
            repetitionList.append(fen[0:endPoint])
            # print(repetitionList)
            for i, item in enumerate(repetitionList):
                repeats = repetitionList.count(item)
                if repeats >= 3:
                    gameOver = True    # enforce repetition rules.
                    reason = "repetition"
            if checkMate:
                print("checkmate")
                gameOver = True
                thinking = False
                if blackClock:
                    blackClock.paused=True
                if whiteClock:
                    whiteClock.paused=True

            elif gameOver:
                print("game over")
                if reason:
                    print(reason)
                thinking = False
                if blackClock:
                    blackClock.paused=True
                if whiteClock:
                    whiteClock.paused=True
            if passPlay:
                rotation = bitboardsObject.getTurn()
                boardObject.rotate(rotation)
                for everyPiece in pieces:
                    everyPiece.rotate(rotation)
                bg = pygame.transform.scale(pygame.image.load("bg" + str(int(rotation == True)) + ".png").convert(), resolution)

            pass
        # print(bitboardsObject.evaluate(pieces, boardObject))


        window.blit(bg, bgrect)
        window.blit(text, text.get_rect())
        window.blit(pgnText, pygame.Rect(0, resolution[1]*0.950, resolution[0]*0.050, resolution[1]*0.100))
        window.blit(fenText, pygame.Rect(0, resolution[1]*0.020, resolution[0]*0.100, resolution[1]*0.100))
        if blackClock and whiteClock:
            if rotation:
                window.blit(whiteClockText, pygame.Rect(resolution[0]*0.730, resolution[1]*0.900, resolution[0]*0.100, resolution[1]*0.100))
                window.blit(blackClockText, pygame.Rect(resolution[0]*0.730, resolution[1]*0.050, resolution[0]*0.100, resolution[1]*0.100))
            else:
                window.blit(blackClockText, pygame.Rect(resolution[0]*0.730, resolution[1]*0.900, resolution[0]*0.100, resolution[1]*0.100))
                window.blit(whiteClockText, pygame.Rect(resolution[0]*0.730, resolution[1]*0.050, resolution[0]*0.100, resolution[1]*0.100))

        if bitboardsObject.promotionLock:   # if there is a promotion lock on
            promoteGroup = pygame.sprite.Group()
            if bitboardsObject.promotingPiece.getType() == 0:
                for i in range(1, 5):
                    promoteGroup.add(objects.promoteButton(bitboardsObject.getTurn(), i, bitboardsObject, boardObject, rotation, resolution))   # make all the selections and add the sprites to a group
            else:
                for i in range(7, 11):
                    promoteGroup.add(objects.promoteButton(bitboardsObject.getTurn(), i, bitboardsObject, boardObject, rotation, resolution))
            promoteGroup.draw(window)   # draw them all
        pieces.update()

        boardObject.draw()
        boardObject.update()
        if initialCoord or nextCoord:   # draw previous move
            functions.renderCoord(initialCoord, boardObject, colour = "#9bc3e5", rotation = rotation)
            functions.renderCoord(nextCoord, boardObject, colour = "#9bc3e5", rotation = rotation)

        if piece and not gameOver:
            if (bitboardsObject.getTurn() and piece.getType() <=5) or ((not bitboardsObject.getTurn() and piece.getType() > 5)):   # show selected piece square
                functions.renderPiece(piece, boardObject, colour = "#fde598", rotation = rotation)
            if outlineDraw:
                functions.renderCoord(functions.boardAbsoluteToBoardCoord(functions.absoluteToRelativeCoords((pygame.mouse.get_pos()), boardObject)), boardObject, rotation= True, width = int(halfsize*0.003), colour = "#aa00ee")

                pass
        pieces.draw(boardObject.getSurface())
        if piece != None:
            boardObject.getSurface().blit(piece.image, piece.rect)

        pygame.display.update()
        # loopCounter+=1
        # not blackClockThread.is_alive()
        if whiteClock or blackClock:
            if not((blackClockThread.is_alive()) or (whiteClockThread.is_alive())) and not gameOver:
                # print("s")
                blackClockThread.start()
                whiteClockThread.start()
        clock.tick()

if __name__ == "__main__":
    main(rotation = True, passPlay = False, perftDepth = 0, aiPlaysBlack = True, aiPlaysWhite = True, blackTime = 0, whiteTime = 0, difficulty = 0)
