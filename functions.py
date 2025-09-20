# from os import environ
# from time import sleep
# import subprocess
import pygame
import bitarray
import objects
# import sys
from stockfish import Stockfish
stockfishFile = open("stockfish.txt", "r")
stockfishPath = stockfishFile.readline().strip()
stockfishParams = stockfishFile.readlines()
stockfish = Stockfish(path=str(stockfishPath))
stockfishFile.close()
# try: ## old code for installing dependencies, now a venv
#     environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # https://stackoverflow.com/questions/51464455/how-to-disable-welcome-message-when-importing-pygame
#     import pygame
#     import bitarray


# except:
#     try:
#         subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
#     except:
#         print("please install requirements with 'pip install [packagename]':")
#         f = open("requirements.txt", "r")
#         print(f.read())
#         f.close()
#         sleep(1)

halfsize = 800 # defining the resolution
resolution = (halfsize, halfsize)
sideSizeX = resolution[0]*0.09
sideSizeY = resolution[1]*0.09
squareSizeTuple = (resolution[0]*0.09, resolution[1]*0.09)
# functions / procedures

def loadBoardHitboxes(boardObject, pieces):    # loads the hitboxes for the pieces on the board
    xAmount = 8
    yAmount = 8
    hitboxes= [[]for h in range(yAmount)]
    yCoord= 0
    for i in range(yAmount):
        xCoord= 0
        for j in range(xAmount):
            currentHitbox= pygame.Rect(xCoord + sideSizeX/2 - 7, yCoord  + sideSizeY/2 - 3.5, 14, 14)
            hitboxes[i].append(currentHitbox)
            pygame.draw.ellipse(boardObject.getSurface(), "green", currentHitbox)
            xCoord+=90
        yCoord+=90
    # print(hitboxes)
    return hitboxes
#    print(hitboxes)
#

def coordsBitboard(coordArray): # converts some coordinates to a bitboard from an array of coordinates
    bitboards = []
    #print(coordArray)
    for i in range(len(coordArray)):
        currentBitArray = bitarray.bitarray(64)
        for j in range(1, len(coordArray[i]), 2):
            # print(coordArray[i][j-1], coordArray[i][j])
            newBB = coordinateBitboard(int(coordArray[i][j-1]), int(coordArray[i][j]))
            currentBitArray = combineTwoBB(currentBitArray, newBB)
        bitboards.append(currentBitArray)
    return bitboards

def coordinateBitboard(xPos, yPos):     # converts one set of coordinates to one bitboard
    currentArray = bitarray.bitarray(64)
    if xPos > 0 and xPos < 9 and yPos > 0 and yPos < 9 :
        bitboardIndex = (xPos-1) + ((yPos-1)*8)
        if bitboardIndex < 64 and bitboardIndex >= 0:
            currentArray[bitboardIndex] = 1
    #    print(currentArray)     #test code
    return currentArray

def bitboardCoordinates(bitArray):      # converts a bitboard to coodinates on my board
    coordList = []
    for i in range(len(bitArray)):
#        print(bitArray[i])
        if int(bitArray[i]) == 1:
            yCoord = (i // 8) + 1
            xCoord = (i % 8) + 1
            coordList.append(xCoord)
            coordList.append(yCoord)
    return coordList

def bitboardCoordinatesAs2D(bitArray):      # converts a bitboard to coodinates on my board
    coordList = []
    for i in range(64):
#        print(bitArray[i])
        if int(bitArray[i]) == 1:
            yCoord = (i // 8) + 1
            xCoord = (i % 8) + 1
            coordList.append((xCoord, yCoord))
    return coordList

def standardDecodeCoord(coord): # decode a square like e4 b6 a2 to number coordinates in my game
    try:
        xCoord = ord(coord[0].lower())-96
        yCoord = 9- int(coord[1])
        return (xCoord, yCoord)
    except:
        print(coord)
        return (-1, -1)

def standardEncodeCoord(coord): # does the opposite of the previous function back to algebraic standard coordinates
    xCoord = coord[0]
    yCoord = coord[1]

    xCoord = chr(xCoord+96)
    yCoord = str(9 - yCoord)
    return (xCoord+yCoord)

def combineTwoBB(bitboardOne, bitboardTwo):     # combines two bitboards into one, for use in combineBitboards but can be for other things.
    newBitboard = bitboardOne | bitboardTwo
    return newBitboard

def combineBitboards(bitboardList):     # combines all bitboards in a list
    i = 0
    if len(bitboardList) > 0:
        newBitboard = bitboardList[i]
        for i in range(len(bitboardList)):
            newBitboard = combineTwoBB(newBitboard, bitboardList[i])
    else:
        newBitboard = bitarray.bitarray(64)
    return newBitboard

def absoluteToRelativeCoords(coords, boardObject): # literal coordinates to ones relative to an rect
    coordsX = coords[0]
    coordsY = coords[1]
    relativeCoordsX = coordsX - boardObject.getRect()[0]
    relativeCoordsY = coordsY - boardObject.getRect()[1]
    relativeCoords = (relativeCoordsX, relativeCoordsY)
    return relativeCoords

def relativeToAbsoluteCoords(coords, boardObject): # again opposite
    coordsX = coords[0]
    coordsY = coords[1]
    absoluteCoordsX = coordsX + boardObject.getRect()[0]
    absoluteCoordsY = coordsY + boardObject.getRect()[1]
    absoluteCoords = (absoluteCoordsX, absoluteCoordsY)
    return absoluteCoords

def checkForClicked(pieces, boardObject):       # code currently checks for when a piece is clicked and prints the type and coordinates of it.
    pointerPos = pygame.mouse.get_pos()
    relativePointerPos = absoluteToRelativeCoords(pointerPos, boardObject)
    for piece in pieces:
        # hitbox = pygame.Rect(piece.getCoords(), squareSizeTuple)
        hitbox = piece.rect
        if hitbox.collidepoint(relativePointerPos):
            # print(piece.getType(), int((piece.getCoords()[0] / sideSizeX) + 1), int((piece.getCoords()[1] / sideSizeY) + 1))
            return piece


def boardAbsoluteToBoardCoord(coord): # converts pixel coordinates to 8x8 coordinates
    return (int((coord[0] / sideSizeX) + 1), int((coord[1] / sideSizeY) + 1))

def boardCoordToBoardAbsolute(coord, resolution): # does the opposite
    return (((coord[0]-1)*(resolution[0]*0.09) + sideSizeX/2), ((coord[1]-1)*(resolution[1]*0.09) + sideSizeY /2))


# def loadPieces(boardObject):    # old early development loadPieces code, loads the basic layout using loops, probably won't work now
#     pieces = pygame.sprite.Group()
#     loadoutFile = open("bitarrays.csv", "r")

#     for i in range(1, 9):
#         if i == 5:
#             piece = objects.piece(5, i, 8, boardObject, resolution, window)
#         elif i == 1 or i == 8:
#             piece = objects.piece(3, i, 8, boardObject, resolution, window)
#         elif i == 2 or i == 7:
#             piece = objects.piece(2, i, 8, boardObject, resolution, window)
#         elif i == 3 or i == 6:
#             piece = objects.piece(1, i, 8, boardObject, resolution, window)
#         else:
#             piece = objects.piece(4, i, 8, boardObject, resolution, window) ##legacy way of loading pieces
#         pieces.add(piece)
#     for i in range(1, 9):
#         piece = objects.piece(0, i, 7, boardObject, resolution, window)
#         pieces.add(piece)
#     for i in range(1, 9):
#         if i == 5:
#             piece = objects.piece(11, i, 1, boardObject, resolution, window)
#         elif i == 1 or i == 8:
#             piece = objects.piece(9, i, 1, boardObject, resolution, window)
#         elif i == 2 or i == 7:
#             piece = objects.piece(8, i, 1, boardObject, resolution, window)
#         elif i == 3 or i == 6:
#             piece = objects.piece(7, i, 1, boardObject, resolution, window)
#         else:
#             piece = objects.piece(10, i, 1, boardObject, resolution, window)
#         pieces.add(piece)
#     for i in range(1, 9):
#         piece = objects.piece(6, i, 2, boardObject, resolution, window)
#         pieces.add(piece)
#     return pieces




def loadPieces(boardObject, bitboardsObject, window, rotation = True): # loads the pieces, this code will return a list of pieces, eventually be able to take in an FEN
    pieces = pygame.sprite.Group()
    pieceBoards = bitboardsObject.getBitboard()
    for i in range(len(pieceBoards)):
        currentBoard = pieceBoards[i]
        for j in range(64):
            if currentBoard[j] == 1:
                xCoord, yCoord = (j % 8)+1, (j // 8)+1
                piece = objects.piece(i, xCoord, yCoord, boardObject, window.get_size(), window, rotation = rotation)
                pieces.add(piece)
    return pieces

def overlapCheck(pieceBoard, boardType, returnBoard): # check if two  bitboards overlap
    newBoard = pieceBoard & boardType
    if not returnBoard:
        overlap = False
        location = 0
        for i in range(64):
            if newBoard[i] == 1:
                overlap = True
                location = i
        return overlap, location
    else:
        return newBoard

def getPieceValue(pieceType): # gets value of a piece type given
    if pieceType == 0 or pieceType == 6:
        pieceValue = 1
    elif pieceType == 1 or pieceType == 7:
        pieceValue = 3
    elif pieceType == 2 or pieceType == 8:
        pieceValue = 3
    elif pieceType == 3 or pieceType == 9:
        pieceValue = 5
    elif pieceType == 4 or pieceType == 10:
        pieceValue = 9
    else:
        pieceValue = 420
    return pieceValue

def takeCheck(piece, bitboardsObject, blackTeam, whiteTeam, pieces): # checks if something should be taken or not
    pieceBoard = piece.getBoard()
    typeBoards = bitboardsObject.getBitboard()
    pieceType = piece.getType()
    took = False
    tookPiece = None

    for i in range(12):
        currentBoard = typeBoards[i]
        if i != pieceType:
            result, location= overlapCheck(pieceBoard, currentBoard, False)
            if result:
                pieceToDieBoard = overlapCheck(pieceBoard, currentBoard, True)
                # print("passed, ", pieceToDieBoard, i)
                # taking = True   # trigger return boolean
                newBoard = aAndNotB(typeBoards[i], pieceToDieBoard)
                bitboardsObject.update(i, newBoard) # update bitboards
                bitboardsObject.resetHalfMoveClock()    # reset half move clock because it's a take
                took = True
                for j in pieces:
                    if j.getBoard()[location] == 1 and j.getType() != pieceType:    # find the took piece
                        pieces.remove(j)
                        tookPiece = j
                if pieceType >= 0 and pieceType <= 5:
                    # print(getPieceValue(i))
                    whiteTeam.pointAdd(value = getPieceValue(i))
                else:
                    blackTeam.pointAdd(value = getPieceValue(i))
    ## en passent code for taking
    passentStatus, passentPieceCoords, enPassentBoard, passentPiece = bitboardsObject.enPassentCheck(pieces)
    # print(passentStatus, passentPieceCoords, enPassentBoard, passentPiece)

    if bitboardsObject.getEnPassentHappened() and passentStatus and passentPiece:
        if pieceBoard == enPassentBoard:
            newBoard = aAndNotB(typeBoards[passentPiece.getType()], passentPiece.getBoard())
            pieces.remove(passentPiece) # remove the piece from the main piece sprite group
            restBoard = bitboardsObject.getBitboard()[passentPiece.getType()]
            newTypeBoard = aAndNotB(restBoard, passentPiece.getBoard())
            bitboardsObject.update(passentPiece.getType(), newTypeBoard)    # update the bitboards
            bitboardsObject.resetHalfMoveClock()    # reset the half move clock because it's a take
            took = True # set whether the piece has been taken
            tookPiece = passentPiece
            if pieceType >= 0 and pieceType <= 5:
                whiteTeam.pointAdd(value = getPieceValue(passentPiece.getType()))
            else:
                blackTeam.pointAdd(value = getPieceValue(passentPiece.getType()))
    if bitboardsObject.getEnPassentHappened():
        bitboardsObject.resetPassent()
    return took, tookPiece  # return information needed for algebraic notation.

def aAndNotB(aBoard, bBoard): # a and not b bitboard, idk why I made it a function
    return aBoard & ~bBoard

def boundsValidate(location, pieceType): # makes sure something is within the actual board
    return not (location[0] > 8 or location[1] > 8 or location[0] < 1 or location[1] < 1)

def validate(movingPiece, oldBoard, newBoard, pieces, bitboardsObject, specials, checkCheck, excludedCoord = (-1, -1), promoteSelection = None): # partially validates piece movments from one square to another
    pieceType = movingPiece.getType()


    if pieceType == 0 or pieceType == 6:
        return pawnCheck(movingPiece, oldBoard, newBoard, pieces, bitboardsObject, specials, checkCheck, promoteSelection)

    elif pieceType == 3 or pieceType == 9: ## check for a rook
        # if specials:
        #     print("validating rook", specials, checkCheck, excludedCoord)
        return rookCheck(movingPiece, oldBoard, newBoard, pieces, bitboardsObject, specials, checkCheck, excludedCoord)

    elif pieceType == 1 or pieceType == 7:
        return bishopCheck(movingPiece, oldBoard, newBoard, pieces, bitboardsObject, specials, checkCheck, excludedCoord)

    elif pieceType == 4 or pieceType == 10:
        return rookCheck(movingPiece, oldBoard, newBoard, pieces, bitboardsObject, specials, checkCheck) or bishopCheck(movingPiece, oldBoard, newBoard, pieces, bitboardsObject, specials, checkCheck)

    elif pieceType == 5 or pieceType == 11:
        return kingCheck(movingPiece, oldBoard, newBoard, pieces, bitboardsObject, specials, checkCheck)

    elif pieceType == 2 or pieceType == 8:
        return knightCheck(movingPiece, oldBoard, newBoard, pieces, bitboardsObject, specials, checkCheck)





def getDirection(pieceCoords, blockingCoords):
    if pieceCoords[0] > blockingCoords[0]:
        direction = "w"
    elif pieceCoords[0] < blockingCoords[0]:
        direction = "e"
    else:
        direction = ""
    if pieceCoords[1] > blockingCoords[1]:
        direction = direction+"s"
    elif pieceCoords[1] < blockingCoords[1]:
        direction = direction+"n"
    else:
        direction = direction+""
    return direction

def getExact (pieceCoords, blockingCoords): # check if the direction is exact or not
    if ((pieceCoords[0] == blockingCoords[0]) or (pieceCoords[1] == blockingCoords[1])):
        exact = True
    elif (abs(blockingCoords[0] - pieceCoords[0]) == abs(blockingCoords[1] - pieceCoords[1])):
        exact = True
    else:
        exact = False
    return exact


def pawnCheck(movingPiece, oldBoard, newBoard, pieces, bitboardsObject, specials, checkCheck, promoteSelection = None): # validates pawn movement
    newCoords = bitboardCoordinates(newBoard)
    oldCoords = bitboardCoordinates(oldBoard)
    pieceType = movingPiece.getType()
    pass1 = False
    pass2 = True
    pass3 = False
    doublePawnPush = False
    disallowedCoords = []
    disallowedCoordsUnfiltered = []
    allowedCoords = []
    if pieceType == 0:
        pawnY = 7
    else:
        pawnY = 2
    pawnStartPos = [list(movingPiece.getPawnStartPos())[0],pawnY]
    if not checkCheck:
        if pieceType > 5:
            if (abs(newCoords[0] - oldCoords[0]) == 1 and newCoords[1] - oldCoords[1] == 1):
                pass1 = True
        else:
            if (abs(oldCoords[0] - newCoords[0]) == 1 and oldCoords[1] - newCoords[1] == 1):
                pass1 = True
    else:
        if pieceType > 5:    # checks standard pawn forward movement
            if (newCoords[0] - oldCoords[0] == 0 and newCoords[1] - oldCoords[1] == 1):
                pass1 = True
                doublePawnPush = False
            elif (newCoords[0] - oldCoords[0] == 0 and newCoords[1] - oldCoords[1] <= 2 and newCoords[1] - oldCoords[1] >= 0) and oldCoords == pawnStartPos:
                pass1 = True
                doublePawnPush = True
        else:
            if (newCoords[0] - oldCoords[0] == 0 and newCoords[1] - oldCoords[1] == -1):
                pass1 = True
                doublePawnPush = False
            elif (newCoords[0] - oldCoords[0] == 0 and newCoords[1] - oldCoords[1] >= -2 and newCoords[1] - oldCoords[1] <= 0) and oldCoords == pawnStartPos:
                pass1 = True
                doublePawnPush = True

        if pieceType <= 5:   # fetches the board for the opposite team so it can take
            oppositeTeamBoards = bitboardsObject.getBitboard()[6:12]
        else:
            oppositeTeamBoards = bitboardsObject.getBitboard()[0:6]
        oppositeTeamBoard = combineBitboards(oppositeTeamBoards)
        disallowedCoordsUnfiltered = bitboardCoordinatesAs2D(oppositeTeamBoard)

    passentStatus, passentPieceCoords, enPassentBoard, passentPiece = bitboardsObject.enPassentCheck(pieces)

    allBoards = bitboardsObject.getBitboard()      # to fix pawns jumping and taking things in front of it
    allBoard = combineBitboards(allBoards)
    if movingPiece.getPawnStartPos()[1] < 4:
        plusOneBoard = coordinateBitboard(oldCoords[0], oldCoords[1] +1)
        plusTwoBoard = coordinateBitboard(oldCoords[0], oldCoords[1] +2)
    else:
        plusOneBoard = coordinateBitboard(oldCoords[0], oldCoords[1] -1)
        plusTwoBoard = coordinateBitboard(oldCoords[0], oldCoords[1] -2)
    if (plusOneBoard & allBoard).any(): # stops forward taking
        disallowedCoords.append(tuple(bitboardCoordinates(plusOneBoard)))
        disallowedCoords.append(tuple(bitboardCoordinates(plusTwoBoard)))
    if (plusTwoBoard & allBoard).any(): # stops forward taking two steps ahead.
        disallowedCoords.append(tuple(bitboardCoordinates(plusTwoBoard)))

    if passentStatus and passentPiece:
        # print("pass 1")
        if pieceType <=5:
            # print("pass 2 white")
            if passentPiece.getType() > 5 and passentPieceCoords[1] == 4:
                # print("pass 3")
                passentCoords = bitboardCoordinates(enPassentBoard)
                # print(passentCoords)
                if (enPassentBoard == newBoard):
                    if (passentCoords[1] == oldCoords[1] - 1) and (passentCoords[0] == oldCoords[0] - 1 or passentCoords[0] == oldCoords[0] + 1):
                        allowedCoords.append(passentCoords)
                        if specials:
                            bitboardsObject.enPassentHappened()
                            # print("passent happened")
                    else:
                        # print("passent didn't happen")
                        if specials:
                            bitboardsObject.enPassentHappenedNot()
                            # bitboardsObject.resetPassent()
        else:
            # print("pass 2 black")
            if passentPiece.getType() <= 5 and passentPieceCoords[1] == 5:
                # print("pass 3")
                passentCoords = bitboardCoordinates(enPassentBoard)
                # print(passentCoords)
                if (enPassentBoard == newBoard):
                    if (passentCoords[1] == oldCoords[1] + 1) and (passentCoords[0] == oldCoords[0] - 1 or passentCoords[0] == oldCoords[0] + 1):
                        allowedCoords.append(passentCoords)
                        if specials:
                            bitboardsObject.enPassentHappened()
                            # print("passent happened")
                    else:
                        # print("passent didn't happen")
                        if specials:
                            bitboardsObject.enPassentHappenedNot()
                            # bitboardsObject.resetPassent()

    for unfilteredCoords in disallowedCoordsUnfiltered: # checks if the pawn is allowed to take a piece diagonal to it
        if pawnStartPos[1] <= 4:
            if (unfilteredCoords[1] == oldCoords[1] + 1) and (unfilteredCoords[0] == oldCoords[0] - 1 or unfilteredCoords[0] == oldCoords[0] + 1):
                allowedCoords.append(unfilteredCoords)
            else:
                disallowedCoords.append(unfilteredCoords)
        else:
            if (unfilteredCoords[1] == oldCoords[1] - 1) and (unfilteredCoords[0] == oldCoords[0] - 1 or unfilteredCoords[0] == oldCoords[0] + 1):
                allowedCoords.append(unfilteredCoords)
            else:
                disallowedCoords.append(unfilteredCoords)

    for coords in disallowedCoords:
        if newCoords == list(coords):
            pass2 = False

    for coords in allowedCoords:
        if newCoords == list(coords):
            pass3 = True

    passentSet = False
    if (pass1 or pass3) and pass2 and doublePawnPush:
        # foundPassent = False
        for piece in pieces:
            if pieceType == 0:
                if piece.getType() == 6:
                    checkingPieceCoords = list(piece.getBoardCoords())
                    if checkingPieceCoords[1] == newCoords[1]:
                        if abs(checkingPieceCoords[0] - newCoords[0]) == 1:

                            if specials:
                                # print("passent possible")
                                bitboardsObject.setPassent(coordinateBitboard(newCoords[0], newCoords[1]+1), tuple(newCoords))
                                passentSet = True
            else:
                if piece.getType() == 0:
                    checkingPieceCoords = list(piece.getBoardCoords())
                    if checkingPieceCoords[1] == newCoords[1]:
                        if abs(checkingPieceCoords[0] - newCoords[0]) == 1:

                            if specials:
                                # print("passent possible")
                                bitboardsObject.setPassent(coordinateBitboard(newCoords[0], newCoords[1]-1), tuple(newCoords))
                                passentSet = True
    if (pass1 or pass3) and pass2 and oldCoords!=newCoords:
        # promotion checking code
        if specials:
            bitboardsObject.resetHalfMoveClock()
            if not passentSet and not bitboardsObject.getEnPassentHappened():
                bitboardsObject.resetPassent()
            if (pawnStartPos[1] > 4 and newCoords[1] == 1) or (pawnStartPos[1] <= 4 and newCoords[1] == 8): # checks for promotion
                if not promoteSelection:    # checks if it's already been specified or not
                    bitboardsObject.promotionPrompt(movingPiece)
                else:
                    movingPiece.setType(promoteSelection, bitboardsObject)
        return True
    else:
        return False


def rookCheck(movingPiece, oldBoard, newBoard, pieces, bitboardsObject, specials, checkCheck, excludedCoord = (-1, -1), flipTeam = False): # validates rook/ half of queen's movement'
    newCoords = bitboardCoordinates(newBoard)
    oldCoords = bitboardCoordinates(oldBoard)
    pieceType = movingPiece.getType()
    disallowedCoords = []

    pass1 = False
    pass2 = True
    if (oldCoords[0] == newCoords[0]) or (oldCoords[1] == newCoords[1]):
        pass1 = True
        ## Criteria 1
    for piece in pieces:
        pieceCoords = piece.getBoardCoords()
        if tuple(pieceCoords) == excludedCoord:
            pieceCoords = (-1, -1)
        if not checkCheck:
            if movingPiece.getType() > 5:
                typeToIgnore = 5
            else:
                typeToIgnore = 11
        else:
            typeToIgnore = -1
        if ((pieceCoords[0] == newCoords[0]) or (pieceCoords[1] == newCoords[1])) and piece.getType() != typeToIgnore:	#if the piece found is blocking this move
            direction = getDirection(oldCoords, pieceCoords)
            allowTake = (pieceType < 6 and piece.getType() > 5) or (pieceType > 5 and piece.getType() < 6)
            if flipTeam:
                allowTake = not allowTake
            if direction == "n":
                checkedy = pieceCoords[1]
                if allowTake or not checkCheck:
                    checkedy +=1    # check if opposite team, then allow to take it.
                while checkedy < 9:
                    disallowedCoords.append((pieceCoords[0], checkedy))
                    checkedy = checkedy + 1
                    ## repeat for all directions using x instead of y where applicable and above 0 instead of less than 9 where applicable
            elif direction == "s":
                checkedy = pieceCoords[1]
                if allowTake or not checkCheck:
                    checkedy -=1
                while checkedy > 0 :
                    disallowedCoords.append((pieceCoords[0], checkedy))
                    checkedy = checkedy - 1
            elif direction == "e":
                checkedx = pieceCoords[0]
                if allowTake or not checkCheck:
                    checkedx +=1
                while checkedx < 9:
                    disallowedCoords.append((checkedx, pieceCoords[1]))
                    checkedx = checkedx + 1
            elif direction == "w":
                checkedx = pieceCoords[0]
                if allowTake or not checkCheck:
                    checkedx -=1
                while checkedx > 0:
                    disallowedCoords.append((checkedx, pieceCoords[1]))
                    checkedx = checkedx - 1
    if tuple(newCoords) in disallowedCoords:
        # if specials:
        #     print(disallowedCoords, newCoords, oldCoords, direction)
        pass2 = False
            ## criteria 2 and 3
    if pass1 and pass2 and boundsValidate(newCoords, pieceType) and oldCoords!=newCoords:
        if pieceType == 3 or pieceType == 9:
            if specials:
                # print("is specials")
                bitboardsObject.castleDeflag(oldCoords, pieceType)
        # else:
            # print(pieceType)
            # if specials:
            #     # print(pieceType, "special")
        if specials:
            bitboardsObject.resetPassent()
        return True

    else:
        # if specials:
        #     print(pass1, pass2, boundsValidate(newCoords, pieceType), oldCoords!=newCoords)
        return False

def bishopCheck(movingPiece, oldBoard, newBoard, pieces, bitboardsObject, specials, checkCheck, excludedCoord = (-1, -1), flipTeam = False): # validates bishop/ half of the queen's movement
    newCoords = bitboardCoordinates(newBoard)
    oldCoords = bitboardCoordinates(oldBoard)
    pieceType = movingPiece.getType()
    disallowedCoords = []
    pass1 = False
    pass2 = True
    if abs(newCoords[0] - oldCoords[0]) == abs(newCoords[1] - oldCoords[1]):
        pass1 = True
    for piece in pieces:
        if not checkCheck:
            if movingPiece.getType() > 5:
                typeToIgnore = 5
            else:
                typeToIgnore = 11
        else:
            typeToIgnore = -1
        pieceCoords = piece.getBoardCoords()
        if tuple(pieceCoords) == excludedCoord: # skip past a certain coordinate
            pieceCoords = (-1, -1)
        # checking to make sure the bishop takes opposite team and blocked past it and just blocked by own team.
        if (abs(newCoords[0] - pieceCoords[0]) == abs(newCoords[1] - pieceCoords[1])) and piece.getType() != typeToIgnore:
            direction = getDirection(oldCoords, pieceCoords)
            checkedx, checkedy = pieceCoords[0], pieceCoords[1]
            allowTake = (pieceType < 6 and piece.getType() >= 6) or (pieceType >= 6 and piece.getType() < 6)
            if flipTeam:
                allowTake = not allowTake
            if direction == "wn":   # north east direction boundaries
                if allowTake or not checkCheck:
                    checkedx -= 1
                    checkedy += 1
                while checkedx < 9 and checkedy < 9:
                    disallowedCoords.append((checkedx, checkedy))
                    checkedx -= 1
                    checkedy += 1
            elif direction == "ws":     # south east direction boundaries
                if allowTake or not checkCheck:
                    checkedx -= 1
                    checkedy -= 1
                while checkedx < 9 and checkedy > 0:
                    disallowedCoords.append((checkedx, checkedy))
                    checkedx -= 1
                    checkedy -= 1
            elif direction == "en": # north west direction boundaries
                if allowTake or not checkCheck:
                    checkedx += 1
                    checkedy += 1
                while checkedx > 0 and checkedy < 9:
                    disallowedCoords.append((checkedx, checkedy))
                    checkedx += 1
                    checkedy += 1
            elif direction == "es":     # south west direction boundaries
                if allowTake or not checkCheck:
                    checkedx += 1
                    checkedy -= 1
                while checkedx > 0 and checkedy > 0:
                    disallowedCoords.append((checkedx, checkedy))
                    checkedx += 1
                    checkedy -= 1
    for coords in disallowedCoords:
        if newCoords == list(coords):
            pass2 = False
            ## criteria 2 and 3
    if pass1 and pass2 and oldCoords!=newCoords:
        if specials and oldCoords != newCoords:
            bitboardsObject.resetPassent()
        return True
    else:
        return False

def kingCheck(movingPiece, oldBoard, newBoard, pieces, bitboardsObject, specials, checkCheck): # validates king's movement
    newCoords = bitboardCoordinates(newBoard)
    oldCoords = bitboardCoordinates(oldBoard)
    pieceType = movingPiece.getType()

    pass1 = False
    pass2 = True
    pass3 = False
    castleFlag = False
    # foundRook = None
    castle = False
    disallowedCoords = []
    recurDisallowedCoords = []
    allowedCoords = []
    if abs(newCoords[0] - oldCoords[0]) <= 1 and abs(newCoords[1] - oldCoords[1]) <= 1:
        pass1 = True
    sameTeamBoards = []
    if pieceType > 5:
        team = False
    else:
        team = True
    if team:
        for i in range(6):
            sameTeamBoards.append(bitboardsObject.getBitboard()[i])
    else:
        for i in range(6, 12):
            sameTeamBoards.append(bitboardsObject.getBitboard()[i])
    sameTeamBoard = combineBitboards(sameTeamBoards)
    disallowedCoords = bitboardCoordinatesAs2D(sameTeamBoard)


    if pass1:   #allows king to take opposing pieces.
        oppositeTeamBoards = []
        if pieceType <= 5:
            team = False
        else:
            team = True
        if team:
            for i in range(6):
                oppositeTeamBoards.append(bitboardsObject.getBitboard()[i])
        else:
            for i in range(6, 12):
                oppositeTeamBoards.append(bitboardsObject.getBitboard()[i])
        oppositeTeamBoard = combineBitboards(oppositeTeamBoards)
        allowedCoords= allowedCoords + bitboardCoordinatesAs2D(oppositeTeamBoard)

    if checkCheck and (pass1 or pass3) and pass2:
        # print(pieceType, checkCheck)
        # print("called here")
        if pieceType == 11:
            coordToAvoid = bitboardCoordinates(bitboardsObject.getBitboard()[5])
        else:
            coordToAvoid = bitboardCoordinates(bitboardsObject.getBitboard()[11])
        # get the location of the opposite king
        if abs(newCoords[0] - coordToAvoid[0]) <= 1 and abs(newCoords[1] - coordToAvoid[1]) <= 1:
            disallowedCoords.append(newCoords)
        # this should see if the king is next to the other king
    startPosPlusOneBoard = bitarray.bitarray(64)
    startPosMinusOneBoard = bitarray.bitarray(64)
    canCastleRight = False
    canCastleLeft = False
    if abs(oldCoords[0] - newCoords[0]) == 2:   # if square is an attempted castle
        # print("castle attempt")
        castleFlag = bitboardsObject.getCastleFlag(newCoords, pieceType)
        # print(castleFlag)
        if castleFlag:
            # print("flag true")
            canCastleRight = True
            canCastleLeft = True
            allBoards = []      # to fix king castling with a piece in the way
            allBoard = combineBitboards(bitboardsObject.getBitboard())
            startPosPlusOneBoard = coordinateBitboard(oldCoords[0] +1, oldCoords[1])    #pain of checking if the castling squares are clear using bitboards the wrong way, of course it can be optimised with logical shifts instead of my converters.
            if (startPosPlusOneBoard & allBoard).any():
                canCastleRight = False
            startPosMinusOneBoard = coordinateBitboard(oldCoords[0] -1, oldCoords[1])
            startPosMinusThreeBoard = coordinateBitboard(oldCoords[0] -3, oldCoords[1])
            if (startPosMinusOneBoard & allBoard).any() or (startPosMinusThreeBoard & allBoard).any():
                canCastleLeft = False
            leftCastleBoard = coordinateBitboard(oldCoords[0] -2, oldCoords[1])
            rightCastleBoard = coordinateBitboard(oldCoords[0] +2, oldCoords[1])
            # print("true")
            if oldCoords[1] == newCoords[1] and ((newBoard == leftCastleBoard) and canCastleLeft) or ((newBoard == rightCastleBoard) and canCastleRight): # castle if clear
                allowedCoords.append(newCoords)
                castle = True # sets the flag for triggering part 2
                # print("castle clear")
                # print('castlefs')
            # else:
                # print("castle not clear")

    possibleMoveBoard = False

    for coords in disallowedCoords:
        # print("disallowed", coords)
        if newCoords == list(coords):
            pass2 = False
            ## criteria 2 and 3

    for coords in allowedCoords:
        # print("allowed", coords)
        if newCoords == list(coords):
            pass3 = True

    if checkCheck and ((pass1 or pass3) and pass2):
        possibleMoveBoards = []
        if pieceType == 5:
            # print(i)
            possibleMoveBoards.append((getPossibleMoves([6, 7, 8, 9, 10], bitboardsObject, pieces, False, False)[0]))
            # print("i run here for white")
            if possibleMoveBoards != []:
                possibleMoveBoard = combineBitboards(possibleMoveBoards)
                recurDisallowedCoords = recurDisallowedCoords + bitboardCoordinatesAs2D(possibleMoveBoard)
        else:
            possibleMoveBoards.append((getPossibleMoves([0, 1, 2, 3, 4], bitboardsObject, pieces, False, False)[0]))
            # print("i run here for black")
            if possibleMoveBoards != []:
                possibleMoveBoard = combineBitboards(possibleMoveBoards)
                recurDisallowedCoords = recurDisallowedCoords + bitboardCoordinatesAs2D(possibleMoveBoard)
        for coords in recurDisallowedCoords:
            if newCoords == list(coords):
                pass2 = False

    if castle:   # if square is an attempted castle part 2 after check check to prevent king passing through check.
        # print(canCastleLeft, canCastleRight)
        if (
            (tuple(oldCoords) not in recurDisallowedCoords) and # can't castle if in check
            (canCastleLeft and (tuple(bitboardCoordinates(startPosMinusOneBoard)) not in (recurDisallowedCoords)) # check if the position is able to be moved into
            and (tuple(newCoords) not in (recurDisallowedCoords)))# and that the castling coords are not in the disallowed coords
        ):
            canCastleLeft = True
        else:
            canCastleLeft = False
        if (
            (tuple(oldCoords) not in recurDisallowedCoords) and # can't castle if in check
            (canCastleRight and (tuple(bitboardCoordinates(startPosPlusOneBoard)) not in (recurDisallowedCoords))
            and (tuple(newCoords) not in (recurDisallowedCoords))) # castle if clear
        ):
            canCastleRight = True
        else:
            canCastleRight = False
                # print('castlefs')'
        if oldCoords[0] - newCoords[0] == 2 and not canCastleLeft:
            pass2 = False
            # print("fail1")
        if newCoords[0] - oldCoords[0] == 2 and not canCastleRight:
            pass2 = False
            # print("fail2")
        else:
            pass
        if specials and pass2:
            bitboardsObject.castleDeflag(oldCoords, pieceType)
            bitboardsObject.castled(newCoords, pieces)

    if (pass1 or pass3) and pass2 and oldCoords!=newCoords:
        if specials:
            bitboardsObject.castleDeflag(oldCoords, pieceType)
            bitboardsObject.resetPassent()
        return True
    else:
        return False

def knightCheck(movingPiece, oldBoard, newBoard, pieces, bitboardsObject, specials, checkCheck): # validates knight's movement'
    newCoords = bitboardCoordinates(newBoard)
    oldCoords = bitboardCoordinates(oldBoard)
    pieceType = movingPiece.getType()
    pass1 = False
    pass2 = True
    disallowedCoords = []
    if (abs(newCoords[0] - oldCoords[0]) == 2 and abs(newCoords[1] - oldCoords[1]) == 1) or (abs(newCoords[0] - oldCoords[0]) == 1 and abs(newCoords[1] - oldCoords[1]) == 2):
        pass1 = True
    sameTeamBoards = []
    if pieceType > 5:
        team = False
    else:
        team = True
    if checkCheck:
        if team:
            for i in range(6):
                sameTeamBoards.append(bitboardsObject.getBitboard()[i])
        else:
            for i in range(6, 12):
                sameTeamBoards.append(bitboardsObject.getBitboard()[i])
    else:
        sameTeamBoards = [bitarray.bitarray(64), bitarray.bitarray(64)]

    sameTeamBoard = combineBitboards(sameTeamBoards)
    disallowedCoords = bitboardCoordinatesAs2D(sameTeamBoard)
    for coords in disallowedCoords:
        if newCoords == list(coords):
            pass2 = False
            ## criteria 2 and 3
    if pass1 and pass2 and oldCoords!=newCoords:
        if specials and oldCoords != newCoords:
            bitboardsObject.resetPassent()
        return True
    else:
        return False

def getPossibleMoves(thePieceOrTypeList, bitboardsObject, pieces, specials, checkCheck): # gets the possible moves mostly
    validBoard = bitarray.bitarray(64)
    validCoords = []
    relevantPieces = []
    for piece in pieces:
        if isinstance(thePieceOrTypeList, list):
            if piece.getType() in thePieceOrTypeList:
                relevantPieces.append(piece)
            else:
                avoid = True
        else:
            if piece == thePieceOrTypeList:
                relevantPieces.append(piece)
            else:
                avoid = True

    for piece in relevantPieces:
        # print('pass1', piece.getType(), thePieceOrType)
        bitboard = ~bitarray.bitarray(64)
        allCoords = bitboardCoordinatesAs2D(bitboard)
        for coord in allCoords:
            # print('pass3')
            if validate(piece, piece.getBoard(), coordinateBitboard(coord[0], coord[1]), pieces, bitboardsObject, specials, checkCheck):
                if (coord != piece.getBoardCoords()):
                    validCoords.append(coord)
                    selectedPiece = piece
    if validCoords != []:
        validBoard = combineBitboards(coordsBitboard(validCoords))

    return validBoard, validCoords

def getCheckingPieces(kingPiece, bitboardsObject, pieces): # gets the checking pieces
    kingCoords = kingPiece.getBoardCoords()
    oldBoard = kingPiece.getBoard()
    opposingBoard = []
    checkers = 0

    directions = []
    if kingPiece.getType() < 6:
        opposingBoard = bitboardsObject.getBitboard()[5:12]
        nonOpposingBoard = bitboardsObject.getBitboard()[0:6]
    else:
        opposingBoard = bitboardsObject.getBitboard()[0:6]
        nonOpposingBoard = bitboardsObject.getBitboard()[5:12]

    # print(opposingBoard)
    opposingBoard = combineBitboards(opposingBoard)
    # print(opposingBoard)
    # print(opposingBoard)
    foundTakingCoords = []
    foundPawn = False
    nonSliderFlag = False
    for i in range(64):
        # print(i)
        foundPawn = pawnCheck(kingPiece, oldBoard, coordinateBitboard((i // 8)+1, (i % 8)+1), pieces, bitboardsObject, False, False) and (((coordinateBitboard((i // 8)+1, (i % 8)+1) & bitboardsObject.getBitboard()[0]).any() and kingPiece.getType() == 11) or (coordinateBitboard((i // 8)+1, (i % 8)+1) & bitboardsObject.getBitboard()[6]).any() and kingPiece.getType() == 5)
        foundRook = rookCheck(kingPiece, oldBoard, coordinateBitboard((i // 8)+1, (i % 8)+1), pieces, bitboardsObject, False, True) and ((coordinateBitboard((i // 8)+1, (i % 8)+1) & bitboardsObject.getBitboard()[3]).any() or (coordinateBitboard((i // 8)+1, (i % 8)+1) & bitboardsObject.getBitboard()[9]).any() or (coordinateBitboard((i // 8)+1, (i % 8)+1) & bitboardsObject.getBitboard()[4]).any() or (coordinateBitboard((i // 8)+1, (i % 8)+1) & bitboardsObject.getBitboard()[10]).any())
        foundBishop = bishopCheck(kingPiece, oldBoard, coordinateBitboard((i // 8)+1, (i % 8)+1), pieces, bitboardsObject, False, True) and ((coordinateBitboard((i // 8)+1, (i % 8)+1) & bitboardsObject.getBitboard()[1]).any() or (coordinateBitboard((i // 8)+1, (i % 8)+1) & bitboardsObject.getBitboard()[7]).any() or (coordinateBitboard((i // 8)+1, (i % 8)+1) & bitboardsObject.getBitboard()[4]).any() or (coordinateBitboard((i // 8)+1, (i % 8)+1) & bitboardsObject.getBitboard()[10]).any())
        foundKnight = knightCheck(kingPiece, oldBoard, coordinateBitboard((i // 8)+1, (i % 8)+1), pieces, bitboardsObject, False, True) and ((coordinateBitboard((i // 8)+1, (i % 8)+1) & bitboardsObject.getBitboard()[2]).any() or (coordinateBitboard((i // 8)+1, (i % 8)+1) & bitboardsObject.getBitboard()[8]).any())
        if foundPawn or foundRook or foundBishop or foundKnight:
            foundTakingCoords.append(((i // 8)+1, (i % 8)+1))
            if foundKnight or foundPawn:
                nonSliderFlag = True
            # print(i // 8, i % 8)
    if foundTakingCoords != [] and (kingPiece.getType() == 5 or kingPiece.getType() == 11):
        # print(foundTakingCoords)
        unfilteredBoard = combineBitboards(coordsBitboard(foundTakingCoords))

        takingBoard = unfilteredBoard & opposingBoard
        for coord in bitboardCoordinatesAs2D(takingBoard):
            directions.append(getDirection(kingCoords, coord))
        directions.append("")
        directions.append("")
    else:
        takingBoard = bitarray.bitarray(64)
        directions = ["", ""]
    checkers = len(bitboardCoordinatesAs2D(takingBoard))
    foundPushCoords = []
    if directions[1] == "" and (takingBoard.any() and not nonSliderFlag):
        for i in range(64):
            # print("foundtaking")
            # print(i)
            newCoords = (i // 8)+1, (i % 8)+1
            newBoard = coordinateBitboard(newCoords[0], newCoords[1])
            checkingDirection = getDirection(kingCoords, newCoords)
            foundRook = rookCheck(kingPiece, oldBoard, newBoard, pieces, bitboardsObject, False, True) and (checkingDirection == directions[0] or checkingDirection == directions[1])
            foundBishop = bishopCheck(kingPiece, oldBoard, newBoard, pieces, bitboardsObject, False, True) and (checkingDirection == directions[0] or checkingDirection == directions[1])
            if foundRook or foundBishop:
                foundPushCoords.append(((i // 8)+1, (i % 8)+1))
                # print(i // 8, i % 8)
        if foundPushCoords != [] and (kingPiece.getType() == 5 or kingPiece.getType() == 11):
            # print(foundCoords)
            unfilteredBoard = combineBitboards(coordsBitboard(foundPushCoords))
            pushBoard = unfilteredBoard & ~combineBitboards(bitboardsObject.getBitboard())
        else:
            pushBoard = bitarray.bitarray(64)
    else:
        pushBoard = bitarray.bitarray(64)
    # print(pushBoard, takingBoard)
    return pushBoard, takingBoard, checkers


def renderBitboard(bitboard, boardObject, colour = "yellow", size = 0.15, rotation = True): # render bitboards as dots on screen
    rects = []
    coords = bitboardCoordinatesAs2D(bitboard)
    if not rotation:
        for coord in coords:
            rects.append(pygame.draw.circle(boardObject.getSurface(), colour, boardCoordToBoardAbsolute((9 -coord[0], 9 -coord[1]), resolution), sideSizeX*size))
    else:
        for coord in coords:
            rects.append(pygame.draw.circle(boardObject.getSurface(), colour, boardCoordToBoardAbsolute(coord, resolution), sideSizeX*size))

    return rects

def renderPiece(piece, boardObject, colour = "yellow", size = 0.15, width = 0 ,rotation = True): # render a piece square as a square on a coordinate
    boardCoords = bitboardCoordinates(piece.getBoard())
    if not rotation:
        boardCoords = [9 -boardCoords[0], 9 - boardCoords[1]]
    coords = boardCoordToBoardAbsolute(boardCoords, resolution)
    coords = (coords[0] - sideSizeX/2, coords[1] - sideSizeY/2)
    pygame.draw.rect(boardObject.getSurface(), colour, pygame.Rect(coords, (int(sideSizeX), int(sideSizeY))), width)

def renderCoord(boardCoords, boardObject, rotation = True, colour = "yellow", size = 0.15, width = 0, ): # just render square on a coordinate
    if not rotation:
        boardCoords = (9-boardCoords[0], 9- boardCoords[1])
    else:
        boardCoords = (boardCoords[0], 0 + boardCoords[1])
    coords = boardCoordToBoardAbsolute(boardCoords, resolution)
    coords = (coords[0] - sideSizeX/2, coords[1] - sideSizeY/2)
    pygame.draw.rect(boardObject.getSurface(), colour, pygame.Rect(coords, (int(sideSizeX), int(sideSizeY))), width)

def fullClickMove(selectedPiece, pointerPos, pieces, bitboardsObject, validBoards, blackTeamObject, whiteTeamObject, rotation = True): # processes a move that is clicked not dragged
    moved = False
    # print(circleRects)
    # print("collide")
    newCoord = boardAbsoluteToBoardCoord(pointerPos)
    if rotation == False:
        newCoord = (9 - newCoord[0], 9 - newCoord[1])
    # print(newCoord)
    moved = selectedPiece.move(newCoord, bitboardsObject, False, pieces, validBoards, blackTeamObject, whiteTeamObject)

    return moved

def getSlidersFromKing(bitboardsObject, pieces, excludedCoord = (-1, -1)): # part of checking for check
    kingPiece = False
    if bitboardsObject.getTurn():
        for piece in pieces:
            if piece.getType() == 5:
                kingPiece = piece
    else:
        for piece in pieces:
            if piece.getType() == 11:
                kingPiece = piece
    if kingPiece:

        kingCoords = kingPiece.getBoardCoords()
        oldBoard = kingPiece.getBoard()
        directions = []
        foundCoords = []
        for i in range(64):
            foundRook = rookCheck(kingPiece, oldBoard, coordinateBitboard((i // 8)+1, (i % 8)+1), pieces, bitboardsObject, False, False, flipTeam = True, excludedCoord=excludedCoord)
            foundBishop = bishopCheck(kingPiece, oldBoard, coordinateBitboard((i // 8)+1, (i % 8)+1), pieces, bitboardsObject, False, True, flipTeam=True, excludedCoord=excludedCoord)
            if foundRook or foundBishop:
                foundCoords.append(((i // 8)+1, (i % 8)+1))
        if foundCoords:
            # print(foundCoords)
            foundBoard = combineBitboards(coordsBitboard(foundCoords))

        else:
            foundBoard = bitarray.bitarray(64)
    else:
        foundBoard = bitarray.bitarray(64)
    return foundBoard

def getPossibleMovesToKing(thePieceOrTypeList, bitboardsObject, pieces, specials, checkCheck, excludedCoord = (-1, -1)): # part of checking for check
    kingPiece = False
    if bitboardsObject.getTurn():
        for piece in pieces:
            if piece.getType() == 5:
                kingPiece = piece
    else:
        for piece in pieces:
            if piece.getType() == 11:
                kingPiece = piece
    if kingPiece:
        validBoard = bitarray.bitarray(64)
        validCoords = []
        for piece in pieces:
            if isinstance(thePieceOrTypeList, list):
                if piece.getType() in thePieceOrTypeList:
                    avoid = False
                else:
                    avoid = True
            else:
                if piece == thePieceOrTypeList:
                    avoid = False
                else:
                    avoid = True

            if not avoid and piece.getType()!= 5 and piece.getType()!=11:

                correctDirection, exact = getDirection(kingPiece.getBoardCoords(), piece.getBoardCoords()), getExact(kingPiece.getBoardCoords(), piece.getBoardCoords())
                # print('pass1', piece.getType(), thePieceOrType)
                bitboard = ~bitarray.bitarray(64)
                allCoords = bitboardCoordinatesAs2D(bitboard)
                for coord in allCoords:
                    # print('pass3')
                    if validate(piece, piece.getBoard(), coordinateBitboard(coord[0], coord[1]), pieces, bitboardsObject, specials, checkCheck, excludedCoord) or tuple(coord) == tuple(piece.getBoardCoords()):
                        if getDirection(coord, piece.getBoardCoords()) == correctDirection and exact:
                            validCoords.append(coord)
                            selectedPiece = piece
                            # print(piece.getBoardCoords())
        if validCoords != []:
            validBoard = combineBitboards(coordsBitboard(validCoords))
        # print("i have ran", recursion,"amount of times", checkCheck)
    else:
        validBoard = bitarray.bitarray(64)
        validCoords = [(-1, -1)]
    return validBoard, validCoords

def getPinnedPieces(pieces, bitboardsObject, excludedCoord = (-1, -1)): # gets all the pinned pieces
    if bitboardsObject.getTurn() == False:
        opposingSliderMoves = (getPossibleMovesToKing([1, 3, 4], bitboardsObject, pieces, False, True, excludedCoord)[0])
    else:
        opposingSliderMoves = (getPossibleMovesToKing([7, 9, 10], bitboardsObject, pieces, False, True, excludedCoord)[0])

    kingSlider = getSlidersFromKing(bitboardsObject, pieces, excludedCoord)

    pinnedPieces = kingSlider & opposingSliderMoves & combineBitboards(bitboardsObject.getBitboard())


    return pinnedPieces, opposingSliderMoves, kingSlider

def getKingDirectionalPin(bitboardsObject, kingSlider, piece): # part of pinned checking
    correctDirection = ""
    pinnedCoord = piece.getBoardCoords()
    turn = bitboardsObject.getTurn()
    if turn:# get the position of the king, this is to filter out other directions for the king ray.
        kingCoords = bitboardsObject.getBitboard()[5]
    else:
        kingCoords = bitboardsObject.getBitboard()[11]

    kingSliderCoords = bitboardCoordinatesAs2D(kingSlider)
    filteredCoords = []
    correctDirection = getDirection(bitboardCoordinates(kingCoords), pinnedCoord)
    for j, kingSliderCoord in enumerate(kingSliderCoords): # for each coordinate detetected as a slider coordinate
        if getDirection(bitboardCoordinates(kingCoords), kingSliderCoord) == correctDirection:
            filteredCoords.append(kingSliderCoord)
        else:
            pass
    bitboardsToCombine = []
    if len(filteredCoords) > 0:
        for i, filteredCoord in enumerate(filteredCoords):
            bitboardsToCombine.append(coordinateBitboard(filteredCoord[0], filteredCoord[1]))
    else:
        bitboardsToCombine = bitarray.bitarray(64), bitarray.bitarray(64)
    finalKingCoords = combineBitboards(bitboardsToCombine)
    canMoveBoard = getRowFromPieceDirection(piece, correctDirection)
    return finalKingCoords, canMoveBoard

def getRowFromPieceDirection(piece, direction): # gets a whole row as a bitboard from a piece and a direction
    # print(direction)
    # print(len(direction))
    if len(direction) >= 2:		# get whether diagonal or not
        if direction[1] == "n":
            vertCoord = 1		# determine how much to move for each axis on each iteration
        else:
            vertCoord = -1
        if direction[0] == "e":
            horizCoord = 1
        else:
            horizCoord = -1
    else:
        if direction == "e":
            vertCoord = 0
            horizCoord = 1
        elif direction == "w":
            vertCoord = 0
            horizCoord = -1
        elif direction == "n":
            vertCoord = 1
            horizCoord = 0
        elif direction == "s":
            vertCoord = -1
            horizCoord = 0
        else:
            vertCoord = 1
            horizCoord = 1
    done = False
    currentCoord = list(piece.getBoardCoords())
    coordsList = []
    while done == False:
        coordsList.append(tuple(currentCoord))  # check forwards
        # print(coordsList)
        currentCoord[0] += horizCoord
        currentCoord[1] += vertCoord
        # print(currentCoord, "forwards")
        if currentCoord[0] > 8 or currentCoord[1] > 8 or currentCoord[0] < 1 or currentCoord[1] < 1:
            done = True
    horizCoord = -1 * horizCoord    # and then go backwards
    vertCoord = -1 * vertCoord
    done = False
    currentCoord = list(piece.getBoardCoords())
    while done == False:
        coordsList.append(tuple(currentCoord))
        # print(coordsList)
        currentCoord[0] += horizCoord
        currentCoord[1] += vertCoord
        # print(currentCoord, "backwards")
        if currentCoord[0] > 8 or currentCoord[1] > 8 or currentCoord[0] < 1 or currentCoord[1] < 1:
            done = True
    boardList = []
    # print(coordsList)
    for coord in coordsList:
        boardList.append(coordinateBitboard(coord[0], coord[1]))
    # print(combineBitboards(boardList))
    return combineBitboards(boardList)

def getLegal(bitboardsObject, piece, pieces): # final function for getting legal moves
    allValids = []
    validBoard = (getPossibleMoves(piece, bitboardsObject, pieces, False, True)[0])    # gets the somewhat pseudo-legal moves
    # print(validBoard.to01())
    validBoards = validBoard
    pinnedPieces, oppSliderMoves, kingSlider= getPinnedPieces(pieces, bitboardsObject)  # gets the pinned pieces and other things for it.
    checkersCount = 0
    pushBoard = bitarray.bitarray(64)
    takingBoard = bitarray.bitarray(64)
    kingPiece = None
    for iterPiece in pieces:
        if (iterPiece.getType() == 5 and piece.getType() <= 5) or (iterPiece.getType() == 11 and piece.getType() > 5):
            kingPiece = iterPiece
    pushBoard, takingBoard, checkersCount = getCheckingPieces(kingPiece, bitboardsObject, pieces)   # checking for checks.
    passentStatus, passentPieceCoords, enPassentBoard, passentPiece = bitboardsObject.enPassentCheck(pieces)
    allBoard = combineBitboards(bitboardsObject.getBitboard())
    if takingBoard.any() and validBoards:   # checks for check

        if checkersCount <= 1:  # checks for double check

            if piece.getType() == 5 or piece.getType() == 11:
                validBoards = validBoards
            else:
                validBoards = validBoards & (takingBoard | pushBoard)
            if passentStatus:   # complicated but not really en passent check fix
                # print(piece.getType(), piece.getBoardCoords(), bitboardCoordinates(enPassentBoard))
                if (piece.getType() == 0 and abs(piece.getBoardCoords()[0] - bitboardCoordinates(enPassentBoard)[0]) == 1 and (piece.getBoardCoords()[1] - bitboardCoordinates(enPassentBoard)[1]) == 1 and bitboardsObject.getTurn()) or (piece.getType() == 6 and abs(piece.getBoardCoords()[0] - bitboardCoordinates(enPassentBoard)[0]) == 1 and (piece.getBoardCoords()[1] - bitboardCoordinates(enPassentBoard)[1]) == -1 and not bitboardsObject.getTurn()):
                    validBoards = validBoards & (takingBoard | pushBoard) | enPassentBoard
        elif piece.getType() == 5 or piece.getType() == 11: # only allow king to move in double check
            # print("double check")
            validBoards = validBoards
        else:   # don't allow any other piece type to move when in double check
            # print("double check empty")
            validBoards = bitarray.bitarray(64)
    if (piece.getBoard() & pinnedPieces).any(): # pinned piece movement
        kingRay, canMoveCoords = getKingDirectionalPin(bitboardsObject, kingSlider, piece)
        # print(bitboardCoordinatesAs2D(kingRay), bitboardCoordinatesAs2D(canMoveCoords))

        validBoards = validBoards & canMoveCoords
    if passentStatus and passentPiece != None:
        passentPinned = getPinnedPieces(pieces, bitboardsObject, excludedCoord = passentPiece.getBoardCoords()) # get pinned pieces without the en passenting piece.
        if (passentPinned[0] & piece.getBoard()).any():  # fix for pins
            validBoards = validBoards &~ enPassentBoard # remove that coordinate from the valid moves list.
    return validBoards, checkersCount

def copyPieceGroup(pieceGroup, bitboards):  # clones a piece group by cloning all pieces into another bitboardObject
    pieces = pygame.sprite.Group()
    for piece in pieceGroup:
        # print(piece.getType())
        newPiece = piece.copy(bitboards)
        # print(newPiece)
        pieces.add(newPiece)
    return pieces

def getListLegalMoves(piece, bitboardsObject, pieces): # used in perft to get a list of legal moves as move objects
    # print(bitboardsObject.getFEN())
    legalBoard = getLegal(bitboardsObject, piece, pieces)[0]   # gets legal bitboard
    allNewCoords = bitboardCoordinatesAs2D(legalBoard) # converts to coordinates
    # print(allNewCoords)
    oldCoords = piece.getBoardCoords()
    moves = []
    copiedPiece = None
    for coords in allNewCoords:
        copyBBO = bitboardsObject.copy()    # makes a copy of the bitboard object
        copiedPieceGroup = copyPieceGroup(pieces, copyBBO)
        for i, copyPiece in enumerate(copiedPieceGroup):
            if piece.getBoardCoords() == copyPiece.getBoardCoords():
                copiedPiece = copyPiece
        if copiedPiece:
            move = objects.move(copiedPiece, copyBBO, oldCoords, coords, copiedPieceGroup, legalBoard)
            moves.append(move)  # adds to list
        else:
            print("oh no")
        # print(move.newLocation)
        # moves.append(move)  # adds to list
        pass
    # print(len(moves))
    return moves


def perft(bitboardsObject, pieces, depth, finalDepth): # standard perft function, missing promotion
    if depth == 0:  # stopping condition
        # counting itself as a move when is a final leaf node.
        return 1
    else:
        moves = []
        count = 0
        for piece in pieces:
            if (piece.getType() > 5 and bitboardsObject.getTurn() == False) or (piece.getType() <= 5 and bitboardsObject.getTurn() == True):
                move = (getListLegalMoves(piece, bitboardsObject, pieces)) # getting all moves
                moves = moves + move
        for i, move in enumerate(moves):
            # print("counting")
            newBitboardsObject = move.getBitboardsObject()
            newPieces = move.getMovedPieces()
            oldCount = count
            # file.write(move.getFEN()+"\n")
            count = count + perft(newBitboardsObject, newPieces, depth-1, finalDepth) # counting them all recursively
            if depth == finalDepth:
                print(move.getOldNewLocation() + ": " +str(count-oldCount))  # prints status
    return count

def getStockfishMove(bitboardsObject, whiteClock = None, blackClock= None): # gets a move from stockfish
    try:
        # sleep(3)
        stockfish.set_fen_position(bitboardsObject.getFEN())
        if whiteClock != None and blackClock!= None:
            stockfishMove = None
            while whiteClock.t > 0 and blackClock.t > 0 and stockfishMove == None:
                stockfishMove = str(stockfish.get_best_move(int(round(whiteClock.t*1000)), int(round(blackClock.t*1000))))
        else:
            stockfishMove =  str(stockfish.get_best_move())
        return stockfishMove
    except:
        print(f"stockfish crashed.\nThe FEN for this position is:\n{bitboardsObject.getFEN()}\n")
        input()
# # def getStockfishMove(bitboardsObject, whiteClock = None, blackClock= None): # debug: mechanical turk mode only works if starting directly from game.py for some reason
# #     move = input("type move: ")
# #     return move

def checkEnd(bitboardsObject, pieces, blackClock = None, whiteClock = None): # check if a game is over
    notFoundEnd = False
    foundMate = False
    reason = "error"
    for piece in pieces:
        if ((piece.getType() <= 5 and bitboardsObject.getTurn()) or (piece.getType() > 5 and not bitboardsObject.getTurn())) and not notFoundEnd:   # checking if the piece is of the correct team and the end has not already been found
            legals = getLegal(bitboardsObject, piece, pieces)
            notFoundEnd = legals[0].any()
            if not notFoundEnd:
                reason = "stalemate"
            # print(legals[0])
            if legals[1] and not notFoundEnd and ((piece.getType() == 5 and bitboardsObject.getTurn()) or (piece.getType() == 11 and not bitboardsObject.getTurn())):  # checking for checkmate with the number of checking pieces.
                foundMate = True
                reason = "checkmate"
    if bitboardsObject.getHalfMoveClock() >= 50:
        notFoundEnd = False # 50 move rule
        reason = "50 move rule"
    if blackClock != None or whiteClock != None:
        if blackClock.ranOutCheck() or whiteClock.ranOutCheck():
            notFoundEnd = False # checks for timer ran out
            reason = "time ran out"
    return not notFoundEnd, foundMate, reason

def getAlgebraic(oldPieceType, newPieceType, validBoards, oldCoords, newCoords, taken, promotedType, checkmate, check, moveNumber, pieces, bitboardsObject): # creates algebraic notation from info given
    algebraic = ""
    castled = False
    whitespace = " "
    promotedString = ""
    if (newPieceType == 5 or newPieceType == 11) and (abs(oldCoords[0] - newCoords[0]) > 1 and oldCoords[1] == newCoords[1]): # check for castling king
        castled = True
        if newPieceType <= 5:
            if newCoords[0] < 4: # check for specific side castling + add move number because white turn
                algebraic = str(moveNumber) + ". " + "O-O-O "
            else:
                algebraic = str(moveNumber) + ". " + "O-O "
        else:
            if newCoords[0] < 4: # check for specific side castling
                algebraic = "O-O-O "
            else:
                algebraic = "O-O "
    if not castled:
        pieceBoard = coordinateBitboard(newCoords[0], newCoords[1])
        ambiguousCoords = []
        ambiguous = False
        for piece in pieces:
            if (int(piece.getType()) == int(newPieceType)) and piece.getBoardCoords() != tuple(oldCoords):
                # print(piece.getType(), pieceType)
                legals = getLegal(bitboardsObject, piece, pieces)[0]
                # print(pieceBoard, legals)
                ambiguityBoard = pieceBoard & legals
                # print(newCoords, bitboardCoordinatesAs2D(legals))
                if ambiguityBoard.any():
                    ambiguousCoords+= bitboardCoordinatesAs2D(ambiguityBoard)
        if ambiguousCoords != [] and (newCoords in ambiguousCoords):
            ambiguous = True

        # ambiguous = (newCoords in bitboardCoordinates(ambiguityBoard))
        # print(ambiguous)
        if oldPieceType == 0 or oldPieceType == 6:	# doing pawn ambiguity checks
            if newCoords[1] == 8 or newCoords[1] == 1:
                # promotedString = getPieceLetter(promotedType)
                if oldPieceType != newPieceType:
                    promotedString = getPieceLetter(newPieceType)
                else:
                    whitespace = ""
            if taken:
                pieceString = standardEncodeCoord(oldCoords)[0]
            else:
                pieceString = ""
        elif ambiguous:
            # print("ambiguous")
            pieceString =  str(getPieceLetter(oldPieceType)) + standardEncodeCoord(oldCoords)
        else:
            pieceString = str(getPieceLetter(oldPieceType))# + standardEncodeCoord(oldCoords)
        if taken:
            takenString = "x"
        else:
            takenString = ""
        newCoordString = standardEncodeCoord(newCoords)
        if checkmate:
            checkString = "#"
        elif check:
            checkString = "+"
        else:
            checkString = ""
        if oldPieceType <= 5:
            algebraic = str(moveNumber) + ". " + (pieceString + takenString + newCoordString + promotedString + checkString + whitespace)
        else:
            algebraic = (pieceString + takenString + newCoordString + promotedString + checkString + whitespace)
    return algebraic

def getPieceLetter(pieceType): # grabs a letter from a piece type
    pieceCodes = ["P", "B", "N", "R", "Q", "K", "p", "b", "n", "r", "q", "k"] # specifying what to look for, for each type of piece
    return pieceCodes[int(pieceType)].upper()

def getPieceNumber(pieceType): # grabs a number from piece type as letter
    pieceCodes = ["P", "B", "N", "R", "Q", "K", "p", "b", "n", "r", "q", "k"] # specifying what to look for, for each type of piece
    for i, val in enumerate(pieceCodes):
        if val == pieceType:
            return i
        else:
            pass
    return None

def setStockfishSkill(number): # unused setting the stockfish skill level
    stockfish.set_skill_level(number)

def checkFENs(fenList): # checks if an FEN is valid or not, not very good.
    bitobj = objects.Bitboards()
    for fen in fenList:
        try:
            # print(fen)
            bitobj = objects.Bitboards(fen)
            bitobj.decodeFEN(fen)   # try decoding, if can't, will error
            bitobj.getFEN()
        except:
            return False
    return True
