from os import environ
from threading import Thread
from oclock import Timer

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # https://stackoverflow.com/questions/51464455/how-to-disable-welcome-message-when-importing-pygame

import bitarray
import functions
import pygame
timer = Timer(interval=1)


class board:                        # defining the board class
    def __init__(self, imagePath, rotationState, window, resolution, rotation = True):
        self.rotationState = rotationState
        self.imagePath = imagePath
        self.resolution = resolution
        self.img = pygame.transform.scale(pygame.image.load(self.imagePath).convert(), (self.resolution[0]*0.72, self.resolution[1]*0.72)).convert()
        self.boardImg= self.img.copy()
        self.window = window

        self.surface = pygame.Surface((round(resolution[0]*0.72), round(resolution[1]*0.72)), flags = pygame.SRCALPHA).convert()
    def draw(self):             # drawing the board either flipped or not
        # if not self.rotationState:
        #     return self.window.blit(self.boardImg, self.surface.get_rect(center= self.window.get_rect().center))
        # else:
        #     self.boardImg=pygame.transform.flip(self.boardImg, False, True).convert()
        #     return self.window.blit(self.boardImg, self.surface.get_rect(center= self.window.get_rect().center))
        return self.window.blit(self.boardImg, self.surface.get_rect(center= self.window.get_rect().center))
    def rotate(self, rotation):
        pass

    def getSurface(self):   #   Getting the surface so it can be used for other things.
        return self.boardImg
    def getRect(self):
        return self.boardImg.get_rect(center= self.window.get_rect().center)
    def setRes(self, res):
        self.resolution = res
    def update(self):
        self.boardImg= self.img.copy()

class move():
    def __init__(self, piece, bitboard, oldLocation, newLocation, pieces, validBoard):  # setting starting attributes
        self.piece = piece
        self.oldLocation = tuple(oldLocation)
        self.newLocation = tuple(newLocation)
        self.movedBitboardObject = bitboard
        self.validBoard = validBoard
        self.movedPieces = pieces
        self.applyMove()

    def applyMove(self):
        self.piece.move(self.newLocation, self.movedBitboardObject, False, self.movedPieces, ~bitarray.bitarray(64), Team("black"), Team("white"))
        # takeCheck(self.piece, self.movedBitboardObject, self.movedPieces)
        self.movedBitboardObject.toggleTurn()

    def getFEN(self):
        return self.movedBitboardObject.getFEN()
    def getBitboardsObject(self):
        return self.movedBitboardObject
    def getMovedPieces(self):
        return self.movedPieces
    def getOldNewLocation(self):
        return functions.standardEncodeCoord(self.oldLocation)+functions.standardEncodeCoord(self.newLocation)

class piece(pygame.sprite.Sprite):      # defining piece class
    def __init__(self, pieceType, xCoord, yCoord, boardObject, resolution, window, rotation = True):
        super(pygame.sprite.Sprite, self).__init__()
        pygame.sprite.Sprite.__init__(self)
        self.pieceType = pieceType
        self.xCoord = xCoord
        self.yCoord = yCoord
        self.board = boardObject
        self.window = window
        self.boardObject = boardObject
        self.resolution = resolution
        self.moving = False
        self.rotation = rotation

        if self.rotation == True:   # sets location based on board rotation True white False black
            self.coords = ((self.xCoord-1)*(self.resolution[0]*0.09), (self.yCoord-1)*(self.resolution[1]*0.09))
        else:
            self.coords = ((9-self.xCoord-1)*(self.resolution[0]*0.09), ((9-self.yCoord)-1)*(self.resolution[1]*0.09))
        self.image = pygame.transform.smoothscale(pygame.image.load(str(self.pieceType)+'.png').convert_alpha(), ((self.resolution[0]*0.09), (self.resolution[1]*0.09)))
        self.rect = pygame.Rect(self.coords, ((self.resolution[0]*0.09),(self.resolution[1]*0.09)))
        self.bitboard = functions.coordinateBitboard(self.xCoord, self.yCoord)
        if self.pieceType > 5:
            self.startingPawnCoords = (self.xCoord, 2)
        else:
            self.startingPawnCoords = (self.xCoord, 7)
        self.killed = False
        self.prevPos = (self.xCoord, self.yCoord)
    def copy(self, bitboardObject): # copy itself with a new bitboardObject
        newPiece = piece(self.pieceType, self.xCoord, self.yCoord, bitboardObject, self.resolution, self.window)
        newPiece.killed = self.killed
        newPiece.prevPos = self.prevPos
        newPiece.startingPawnCoords = self.startingPawnCoords
        newPiece.coords = self.coords
        newPiece.bitboard = self.bitboard
        return newPiece
    def setRes(self, res):  # setting the resolution, I attepted scaling one time, it was too much work and not worth it
        self.resolution = res
    def rotate(self, rotation): # rotates position for pass and play
        self.rotation = rotation

        if self.rotation == True:
            self.coords = ((self.xCoord-1)*(self.resolution[0]*0.09), (self.yCoord-1)*(self.resolution[1]*0.09))
        else:
            self.coords = ((9-self.xCoord-1)*(self.resolution[0]*0.09), ((9-self.yCoord)-1)*(self.resolution[1]*0.09))
    def getType(self):  # returns its type
        return self.pieceType
    def setType(self, typeNo, bitboardsObject, addPGN = False): # set it's type to a new one, option to add the pgn for promotion
        notSelfBoard = ~ self.bitboard
        restBoard = bitboardsObject.getBitboard()[self.pieceType]
        newTypeBoard = notSelfBoard & restBoard
        bitboardsObject.update(self.pieceType, newTypeBoard)
        self.pieceType = typeNo
        if addPGN:
            bitboardsObject.pgn += functions.getPieceLetter(self.pieceType) + " "
        # bitboardsObject.update(self.pieceType, newTypeBoard)



        self.image = pygame.transform.smoothscale(pygame.image.load(str(self.pieceType)+'.png').convert_alpha(), ((self.resolution[0]*0.09), (self.resolution[1]*0.09)))
    # simple getter methods
    def getCoords(self):
        return self.coords
    def getRect(self):
        return self.rect
    def getBoard(self):
        return self.bitboard
    def getPawnStartPos(self):
        return self.startingPawnCoords
    def setBoard(self, board):  # sets the bitboard of the piece to a new one
        # print('newboard', board)
        self.bitboard = board
        done = False
        for i in range(64): # changes its coordinates to new one
            if board[i] == 1 and not done:
                self.xCoord, self.yCoord = functions.bitboardCoordinates(board)
                done = True
            else:
                self.killed = True
    def update(self): # update position for rendering
        if not self.killed:
            self.rect = pygame.Rect(self.coords, ((self.resolution[0]*0.09),(self.resolution[1]*0.09)))
            self.bitboard = functions.coordinateBitboard(self.xCoord, self.yCoord)
        else:
            self.kill()
    def move(self, location, bitboardsObject, ghost, pieces, validCoords, blackTeam = False, whiteTeam = False, promotionSelection = None): # moving itself either dragging it or real moves
        if (self.pieceType <= 5 and bitboardsObject.getTurn() == True) or (self.pieceType > 5 and bitboardsObject.getTurn() == False):
            if not ghost:   # move properly if not just a drag
                prevX = self.xCoord
                prevY = self.yCoord
                moved = True
                if not functions.boundsValidate(location, self.pieceType):
                    location = prevX, prevY
                    moved = False
                else:
                    if not (functions.coordinateBitboard(location[0], location[1]) & validCoords).any():
                        location = prevX, prevY
                        moved = False
                    else:
                        moved = True
                oldBitboardObject = bitboardsObject.copy()
                copiedPieceGroup = functions.copyPieceGroup(pieces, oldBitboardObject)
                oldType = self.pieceType

                if (prevX, prevY) == location:
                    moved = False
                    # print("no move")

                if moved:
                    # update bitboard position
                    valid = functions.validate(self, self.bitboard, functions.coordinateBitboard(location[0], location[1]), pieces, bitboardsObject, True, True, promoteSelection = promotionSelection)    # enacts any special stuff
                    if not valid:
                        print(f"not valid, fen = {bitboardsObject.getFEN()}")
                    self.xCoord, self.yCoord = location
                    oldBoard = self.bitboard
                    self.bitboard = functions.coordinateBitboard(self.xCoord, self.yCoord) # sets its own board to the new position
                    self.rotate(self.rotation)

                    typeBoard = bitboardsObject.getBitboard()[self.pieceType]
                    minusTypeBoard = functions.aAndNotB(typeBoard, oldBoard) # gets the old position removed from the board of its type
                    newTypeBoard = minusTypeBoard | self.bitboard   # adds the new position to the removed board of its type
                    took, tookPiece = functions.takeCheck(self, bitboardsObject, blackTeam, whiteTeam, pieces)
                    # bitboardsObject.castleDeflag((prevX, prevY))
                    self.prevPos = (prevX, prevY)

                    bitboardsObject.update(self.pieceType, newTypeBoard)    # updates the bitboard object with the new position
                    bitboardsObject.pgn += functions.getAlgebraic(oldType, self.pieceType, bitarray.bitarray(64), self.prevPos, location, took, self.pieceType, False, False, bitboardsObject.getMoveCounter(), copiedPieceGroup, oldBitboardObject)
                    # debugFile = open("debugtext.txt", "a")
                    # debugFile.write(functions.getAlgebraic(oldType, self.pieceType, bitarray.bitarray(64), self.prevPos, location, took, "10", False, False, bitboardsObject.getMoveCounter(), copiedPieceGroup, oldBitboardObject) + " ")
                    # debugFile.close()

                # print("returning moved", moved)
                else:
                    self.rotate(self.rotation)
            else:   # simple dragging code
                moved = False
                self.coords = (location[0] - (self.resolution[0]*0.09)/2, location[1] - (self.resolution[1]*0.09)/2)

        else:
            moved = False
        return moved
    def teleport(self, location, bitboardsObject): # teleports a piece indiscriminantly
                self.xCoord, self.yCoord = location
                self.rotate(self.rotation)
                # update bitboard position
                oldBoard = self.bitboard
                self.bitboard = functions.coordinateBitboard(self.xCoord, self.yCoord)
                typeBoard = bitboardsObject.getBitboard()[self.pieceType]
                minusTypeBoard = functions.aAndNotB(typeBoard, oldBoard)
                newTypeBoard = minusTypeBoard | self.bitboard
                bitboardsObject.update(self.pieceType, newTypeBoard)
    def getBoardCoords(self):
        return (self.xCoord, self.yCoord)


class Bitboards: # class for controlling the game's state
    def __init__(self, fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        # self.bitboards = coordsBitboard(self.loadPieces())
        self.bitboards, self.whiteTurn, self.leftWhiteCastle, self.leftBlackCastle, self.rightWhiteCastle, self.rightBlackCastle, self.enPassentBoard, self.passentPieceCoords, self.halfMoveClock, self.fullMoveClock = self.decodeFEN(fen)
        # print(self.bitboards)
        # self.passentPiece = None
        self.enPassentHappenedATT = False
        self.plyCounter = 0
        self.promotionLock = False
        self.promotingPiece = None
        self.pgn = ""
        self.positionInGame = 0
        self.fenList = []

    def copy(self):
        copiedBitboardObject = Bitboards(self.getFEN())
        copiedBitboardObject.enPassentHappenedATT = self.enPassentHappenedATT
        copiedBitboardObject.halfMoveClock = self.halfMoveClock
        copiedBitboardObject.fullMoveClock = self.halfMoveClock
        return copiedBitboardObject
    def getBitboard(self):
        return self.bitboards

    def toggleTurn(self):
        if self.whiteTurn:
            self.whiteTurn = False
        else:
            self.fullMoveClock+=1

            self.whiteTurn = True
        self.halfMoveClock +=1
        self.plyCounter +=1

    def promotionPrompt(self, piece):
        self.promotionLock = True
        self.promotingPiece = piece
    def getMoveCounter(self):
        return self.fullMoveClock

    def getHalfMoveClock(self):
        return self.halfMoveClock

    def getPlyCounter(self):
        return self.plyCounter

    def resetHalfMoveClock(self):
        self.halfMoveClock = -1    # resets the halfmove clock for the 50 move rule

    def getTurn(self):
        return self.whiteTurn

    def setState(self, fen):
        self.bitboards, self.whiteTurn, self.leftWhiteCastle, self.leftBlackCastle, self.rightWhiteCastle, self.rightBlackCastle, self.enPassentBoard, self.passentPieceCoords, self.halfMoveClock, self.fullMoveClock = self.decodeFEN(fen)

    # def loadPieces(self):
    #     arrayOfCoords = []
    #     with open("bitarrays.csv", newline='') as file:
    #         csvLists = csv.reader(file)
    #         for row in csvLists:
    #             # print(row)
    #             arrayOfCoords.append(row)
    #         file.close()
    #         return arrayOfCoords

    def overlapCheck(self, pieceBoard, boardType, returnBoard = True):
        newBoard = pieceBoard ^ boardType
        if not returnBoard:
            overlap = False
            for i in range(64):
                if newBoard[i]:
                    overlap = True
                return overlap
            else:
                return newBoard

    def update(self, pieceType, newBoard):  # changes the piece type's bitboard to a new one
        # print(newBoard)
        self.bitboards[pieceType] = newBoard

    def castleDeflag(self, coordinates, pieceType): # automatically  removes the flag(s) for castling with given piece type and coordinates.
        if pieceType > 5 and pieceType < 11:
            if coordinates[0] <= 5:
                self.leftBlackCastle = False
            elif coordinates[0] > 5:
                self.rightBlackCastle = False
        elif pieceType == 11:
            self.leftBlackCastle = False
            self.rightBlackCastle = False
        elif pieceType < 5:
            if coordinates[0] <= 5:
                self.leftWhiteCastle = False
            elif coordinates[0] > 5:
                self.rightWhiteCastle = False
        else:
            self.leftWhiteCastle = False
            self.rightWhiteCastle = False
        # print("deflagged")

    def getCastleFlag(self, coordinates, pieceType):    # gets if something can castle or not from the coordinates.
        if coordinates[1] <= 4 and pieceType > 5:
            if coordinates[0] < 5:
                return self.leftBlackCastle
            else:
                return self.rightBlackCastle
        elif coordinates[1] > 5 and pieceType <= 5:
            if coordinates[0] < 5:
                return self.leftWhiteCastle
            else:
                return self.rightWhiteCastle
        else:
            return False

    def castled(self, newCoords, pieces): # teleports the rook correctly when castling
        foundRook = None
        foundCoords = []
        for piece in pieces:
            rookCoords = list(piece.getBoardCoords())

            if newCoords[1] >= 4: # checks vertical side of the board
                if (abs((rookCoords[0]) - newCoords[0]) <= 2) and piece.getType() ==  3 and rookCoords[1] == newCoords[1]:
                    foundRook = piece
                    foundCoords = foundRook.getBoardCoords()
                    if foundCoords[0] <=4:  # checks horizontal side of the board
                        foundRook.teleport((foundCoords[0] + 3, foundCoords[1]), self)
                    else:
                        foundRook.teleport((foundCoords[0] - 2, foundCoords[1]), self)

            else:   # ditto for the other side
                if (abs((rookCoords[0]) - newCoords[0]) <= 2) and piece.getType() ==  9 and rookCoords[1] == newCoords[1]:
                    foundRook = piece
                    foundCoords = foundRook.getBoardCoords()
                    # print(foundCoords)
                    if foundCoords[0] <=4:
                        foundRook.teleport((foundCoords[0] + 3, foundCoords[1]), self)
                    else:
                        foundRook.teleport((foundCoords[0] - 2, foundCoords[1]), self)

    def enPassentCheck(self, pieces):   # checks if en passent has happened and the details
        # print("checked")
        passentPiece = None
        for piece in pieces:
            if piece.getBoardCoords() == self.passentPieceCoords and not passentPiece:
                passentPiece = piece
        # if self.enPassentBoard.any():
            # print(self.enPassentBoard)
        return self.enPassentBoard.any(), self.passentPieceCoords, self.enPassentBoard, passentPiece

    def setPassent(self, newBoard, pieceCoords): # triggers en passent flag on
        # print("passent set")
        self.enPassentBoard = newBoard
        self.passentPieceCoords = pieceCoords

    def enPassentHappened(self):    # says en passent happened
        self.enPassentHappenedATT = True
        # self.resetPassent()

    def enPassentHappenedNot(self): # says en passent didn't happen
        self.enPassentHappenedATT = False
        # self.resetPassent()

    def getEnPassentHappened(self): # check if en passent has happened
        return self.enPassentHappenedATT

    def resetPassent(self): # resets en passent to not happened
        # print("passent reset")
        self.enPassentBoard = bitarray.bitarray(64)
        self.passentPieceCoords = None
        self.passentMove = -1
        self.enPassentHappenedATT = False


    def decodeFEN(self, fenCode):   # decodes an FEN code to bitboards and flags for my game
        pieceCodes = ["P", "B", "N", "R", "Q", "K", "p", "b", "n", "r", "q", "k"] # specifying what to look for, for each type of piece
        rankBoards = []
        leftWhiteCastle = False
        enPassentBoard = bitarray.bitarray(64)
        passentPieceCoords = (-1, -1)
        leftBlackCastle = False
        rightWhiteCastle = False
        rightBlackCastle = False
        halfMoveCounter = False
        fullMoveCounter = False
        pieceBoards = []
        currentTurn = True
        point = ""
        for i in range(len(fenCode)):
            if point == "" and fenCode[i] == " ":
                point = i
        if point:
            placementField = fenCode[0:point]# finding the placement field.
            ranks = placementField.split("/") # getting the individual ranks of the placement field
            newRanks = []
            for h, rank in enumerate(ranks):
                # print(rank)
                newRank = ""
                for i, value in enumerate(rank):
                    # print(i)
                    if value.isnumeric():
                        # print(value, "bb")
                        newRank = newRank +( "1" * (int(value))) # unrolling the numbers for the FEN
                        # print(newRank)
                    else:
                        # print(value, "aa")
                        newRank = newRank + value
                        # print(newRank + value)
                newRanks.append(newRank)
            newRanks = "".join(newRanks)
            # print(newRanks)
            for i in range(12):
                for j in range(64):
                    bitrank = ""
                    if newRanks[j] == pieceCodes[i]: #checking if the character found is one belonging to the current type iterating
                        bitrank = bitrank + "1"
                    else:
                        bitrank = bitrank + "0"
                    rankBoards.append(bitrank)

                pieceBoards.append(bitarray.bitarray("".join(rankBoards))) #joining the ranks together into one bitboard and then adding them to a list of bitboards, like my current code.
                rankBoards = []

            activeColour = fenCode[point+1]
            if activeColour.lower() == "w":
                currentTurn = True
            elif activeColour.lower() == "b":
                currentTurn = False
            else:
                currentTurn = True

            castlePoint = point + 3
            endPoint = None
            for i, val in enumerate(fenCode[castlePoint::]):
                # print(val)
                if val == " " and not endPoint:
                    endPoint = castlePoint + i
                    # print("found")
            if endPoint:
                # print(endPoint)
                castleSection = fenCode[castlePoint:(endPoint)]
                # print(castleSection)
                if "k" in castleSection:
                    rightBlackCastle = True
                    # print("k")
                if "K" in castleSection:
                    rightWhiteCastle = True
                    # print("K")
                if "q" in castleSection:
                    leftBlackCastle = True
                    # print("q")
                if "Q" in castleSection:
                    leftWhiteCastle = True
                    # print("Q")
                passentPoint = endPoint+1
                passentEnd = passentPoint + 2
                if fenCode[passentPoint] != "-":
                    passentEnd+=1
                    # print(fenCode[passentPoint:passentEnd])
                    # print(fenCode[passentEnd::])
                    passentCoords = functions.standardDecodeCoord(fenCode[passentPoint:passentEnd])
                    enPassentBoard = functions.coordinateBitboard(passentCoords[0], passentCoords[1])
                else:
                    passentCoords = (0, 0)

                    enPassentBoard = bitarray.bitarray(64)
                if passentCoords[1] > 4:
                    newY = passentCoords[1] - 1
                else:
                    newY = passentCoords[1] + 1
                passentPieceCoords = (passentCoords[0], newY)
                halfMovePoint = None
                for i, val in enumerate(fenCode[passentEnd::]):
                    if val == " " and not halfMovePoint:
                        halfMovePoint = passentEnd + i
                halfMoveCounter = int(fenCode[passentEnd:halfMovePoint])
                fullMoveCounter = int(fenCode[halfMovePoint::])


        return pieceBoards, currentTurn, leftWhiteCastle, leftBlackCastle, rightWhiteCastle, rightBlackCastle, enPassentBoard, passentPieceCoords, halfMoveCounter, fullMoveCounter

    def replaceBitboardWithLetters(self, currentBoard, pieceType):  # part of creating an FEN replacing each bitboard to have letters for the type of piece
        pieceCodes = ["P", "B", "N", "R", "Q", "K", "p", "b", "n", "r", "q", "k"] # specifying what to replace with, for each type of piece
        currentBoard = currentBoard.to01() # converts a bitboard to string of 1s and 0s
        # print(currentBoard, pieceCodes[pieceType])
        newBoard = ""
        for j in range(64):
            if currentBoard[j] == "1":
                newBoard = newBoard + pieceCodes[pieceType] # replace with correct letter if found
            else:
                newBoard = newBoard + "0"
            # print(newBoard, j, pieceType)
        return newBoard

    def mergeFENunrolled(self, newBoard1, newBoard2):   # merges all the boards with the letters together
        mergeBoard = ""
        for i in range(64):
            if not newBoard1[i].isnumeric(): # if either is a letter, add them to the new merged board
                mergeBoard = mergeBoard + newBoard1[i]
            elif not newBoard2[i].isnumeric():
                mergeBoard = mergeBoard + newBoard2[i]
            else:
                mergeBoard = mergeBoard + "0"
        return mergeBoard

    def rollUpFEN(self, rank): # merges the numbers together to get shortened FEN so like 00000000 to 8 or 000P0000 to 3P4
        numCount = 0
        newBoard = ""
        # print(rank)
        for i in range(8):
            if rank[i].isnumeric():
                numCount += 1   # don't add to the string if a number, adding the number is done later
            else:
                if numCount > 0:
                    newBoard = newBoard + str(numCount) # add the count if there is a count
                    numCount = 0    # reset to 0
                newBoard = newBoard + rank[i]
        if numCount > 0:    # add any remaining number on
            newBoard = newBoard + str(numCount)
        return newBoard

    def convertToFEN(self):     # function to convert bitboards to FEN position
        boards=self.getBitboard()
        letterBoards = []
        for i in range(12):
            board = boards[i]
            letterBoards.append(self.replaceBitboardWithLetters(board, i))
        # print(letterBoards)
        mergedBoard = letterBoards[0]
        for i in range(1,12):
            # print(letterBoards)
            mergedBoard = self.mergeFENunrolled(letterBoards[i], mergedBoard)
            # print(mergedBoard)
        splitFEN = []
        for i in range(8, 72, 8):   # split the merged board into 8 separate segments.
            # print(mergedBoard[i-8:i])
            splitFEN.append(mergedBoard[i-8:i])

        splitFENRolled = []
        for i in range(8):
            splitFENRolled.append(self.rollUpFEN(splitFEN[i]))
        # print(splitFENRolled)
        positionalFEN = ""
        for i in range(8):
            positionalFEN = positionalFEN + "/" + splitFENRolled[i] # putting it back together.
        positionalFEN = positionalFEN[1::]
        return positionalFEN

    def getFEN(self):   # adds the extra data on to the FEN for castling and en passent and such
        fen = self.convertToFEN()
        if self.getTurn():
            fen+= " w "
        else:
            fen+= " b "
        if self.rightWhiteCastle:
            fen += "K"
        if self.leftWhiteCastle:
            fen += "Q"
        if self.rightBlackCastle:
            fen+= "k"
        if self.leftBlackCastle:
            fen+= "q"
        if not (self.rightWhiteCastle or self.leftWhiteCastle or self.rightBlackCastle or self.leftBlackCastle):
            fen += "-"

        if self.enPassentBoard.any():
            fen = fen + " " + functions.standardEncodeCoord(functions.bitboardCoordinates(self.enPassentBoard))
        else:
            fen += " -"

        fen = fen + " " + str(self.halfMoveClock) + " " + str(self.fullMoveClock)


        return fen

    def evaluate(self, pieces): # old evaluation code, unused due to implementing stockfish
        # defines the weights of each piece and mobility
        kingWt = 100
        queenWt = 9
        rookWt = 7
        knightWt = 6
        bishopWt = 4
        pawnWt = 1
        mobilityWt = 1

        bitboards = self.getBitboard()
        counts = []
        for i in range(12):
            counts.append(bitboards[i].count()) # gets count of pieces
        whiteCount = 0
        blackCount = 0
        currentBoard = bitarray.bitarray(64)
        for piece in pieces:    # gets the available moves for the pieces.
            legals = functions.getLegal(self, piece, pieces)
            if piece.getType() <= 5:
                whiteCount += legals.count()
                currentBoard = currentBoard | legals
            elif piece.getType() > 5:
                blackCount += legals.count()
        counts.append(whiteCount)
        counts.append(blackCount)
        # input()

        materialScore = kingWt * (counts[5] - counts[11]) \
            + queenWt * (counts[4] - counts[10]) \
            + rookWt * (counts[3] - counts[9]) \
            + knightWt * (counts[2] - counts[8]) \
            + bishopWt * (counts[1] - counts[7]) \
            + pawnWt * (counts[0] - counts[6])
            # adds the weights and counts together into a material score

        mobilityScore = mobilityWt * (counts[12] - counts[13])  # gethers the mobility score
        # print(counts)
        # print(materialScore, mobilityScore)

        if self.getTurn() == True:
            turn = +1
        else:
            turn = -1
        fullScore = (materialScore + mobilityScore) * turn # multiples by -1 for relative turn
        return fullScore

    def step(self, operation, boardObject, window, pieces): # steps through a game for replay mode
        if (self.positionInGame + operation < len(self.fenList)) and (self.positionInGame + operation >= 0):    # check bounds
            self.positionInGame += operation
        # print(self.positionInGame)
        fen = self.fenList[self.positionInGame]
        # print(fen)
        self.bitboards, self.whiteTurn, self.leftWhiteCastle, self.leftBlackCastle, self.rightWhiteCastle, self.rightBlackCastle, self.enPassentBoard, self.passentPieceCoords, self.halfMoveClock, self.fullMoveClock = self.decodeFEN(fen)
        # pieces.clear(boardObject.getSurface(), window)
        pieces = functions.loadPieces(boardObject, self, window, True)
        return pieces



class Team:     # simple team class for points for when taking a piece
    def __init__(self, name):
        self.points = 0
        self.name = name

    def getPoints(self):
        return self.points

    def pointAdd(self, value):
        self.points += value
        # print(self.name,"team has",self.points,"points.")
        return self.points

class threadThatReturns(Thread): # modified from https://jackwhitworth.com/blog/return-values-from-a-python-thread/
    def __init__(self, target):
        Thread.__init__(self)
        self.target = target
        self.result = None

    def run(self):
        self.result = self.target()


class chessClock:   # class for my chess clock
    def __init__(self, time, paused = False):
        self.t = time
        self.paused = paused
        self.timer = Timer(interval=0.01)  # initialising the oclock timer
        self.killed=False
        self.end = False
        # if self.paused:
        #     self.timer.pause()
        # else:
        #     self.timer.resume()
    # @loop(timer)
    def startClock(self):
        self.t += 0.01
        while self.t > 0 and not self.killed:   # terminating condition for exiting.
            self.refreshClock() # check for pause
            # print(str(self.t).zfill(2))
            self.t =round(self.t - 0.01, 3)    # removing 10ms from the countdown. The round accounts for floating point errors in some CPUs.
            self.timer.checkpt()    # wait until the rest of the 10ms is over
        self.end = True
        return True

    def refreshClock(self):
        if self.paused: # pause the timer if paused
            self.timer.pause()
        else:
            self.timer.resume()
    def toggleClock(self):
        self.paused = not self.paused

    def addTime(self, value):
        self.t += int(value)
    def ranOutCheck(self):  # checks if 0 and says if it has ran out or not
        if self.t > 0:
            return False
        else:
            return True
    def kill(self): # allow the while loop to be killed by the host program
        self.killed = True

# clock = chessClock(30)
# clockThread = Thread(target=clock.startClock)
# clockThread.start()
# while True:
#     theinput = input("type toggle to toggle\n")
#     if theinput == "toggle":
#         clock.toggleClock()

class promoteButton(pygame.sprite.Sprite):  # a class for promoting a piece by a player, the buttons that show up
    def __init__(self, team, type, bitboardsObject, boardObject, rotation, resolution):
        pygame.sprite.Sprite.__init__(self)
        self.team = team    # defining attributes
        self.resolution = resolution
        self.rotation = rotation
        self.type = type
        self.bitboardsObject = bitboardsObject
        self.promotingPiece = self.bitboardsObject.promotingPiece
        if self.type <= 5:  # setting the position on the screen
            self.xCoord = self.promotingPiece.getBoardCoords()[0] + self.type - 2

        else:
            self.xCoord = self.promotingPiece.getBoardCoords()[0] + 11- self.type - 2

        if self.rotation:
            if self.type <= 5:
                self.yCoord = self.promotingPiece.getBoardCoords()[1] - 1
            else:
                self.yCoord = self.promotingPiece.getBoardCoords()[1] + 4
        else:
            if self.type <= 5:
                self.yCoord = self.promotingPiece.getBoardCoords()[1] - 4
            else:
                self.yCoord = self.promotingPiece.getBoardCoords()[1] + 1
        self.image = pygame.transform.smoothscale(pygame.image.load(str(self.type)+'.png').convert_alpha(), ((self.resolution[0]*0.07), (self.resolution[1]*0.07))) # setting texture
        if self.rotation == True:
            self.coords = ((self.xCoord-1)*(self.resolution[0]*0.07), (self.yCoord-1)*(self.resolution[1]*0.07) - 20)
        else:
            self.coords = ((9-self.xCoord-1)*(self.resolution[0]*0.07), ((9-self.yCoord)-1)*(self.resolution[1]*0.07) - 20)

        self.coords = functions.relativeToAbsoluteCoords(self.coords, boardObject)
        self.rect = pygame.Rect(self.coords, ((self.resolution[0]*0.07),(self.resolution[1]*0.07)))


    def clicked(self):
        self.promotingPiece.setType(self.type, self.bitboardsObject, True)    # sets the type of the object
        self.promotingPiece.teleport(self.promotingPiece.getBoardCoords(), self.bitboardsObject)    # makes it work with the bitboards
        self.bitboardsObject.promotionLock = False # turn off the promotion lock
        self.bitboardsObject.toggleTurn()   # swap the turns

class stepButton(pygame.sprite.Sprite):     # a button for stepping through a game, used for replayGame
    def __init__(self, bitboardsObject, boardObject, window, pieces, operation = 1, coords = (300, 40), rotation = True, resolution = (800, 800)):
        pygame.sprite.Sprite.__init__(self)
        self.operation = operation
        self.bitboardsObject = bitboardsObject
        self.pieces = pieces
        self.coords = (resolution[0]*(0.750+0.030*operation), resolution[1]*0.010)
        self.boardObject = boardObject
        self.window = window
        self.resolution = resolution
        ## sprite initialisation
        if str(self.operation) == "-1":
            imageName = "leftArrow.png"
            # print(self.operation)
        else:
            imageName = "rightArrow.png"
        self.image = pygame.transform.smoothscale(pygame.image.load(str(imageName)).convert(), ((self.resolution[0]*0.07), (self.resolution[1]*0.07))) # setting placeholder texture for now        self.rect = pygame.Rect(self.coords, ((self.resolution[0]*0.07),(self.resolution[1]*0.07)))
        self.rect = pygame.Rect(self.coords, ((self.resolution[0]*0.07),(self.resolution[1]*0.07)))


    def clicked(self):
        pieces = self.bitboardsObject.step(self.operation, self.boardObject, self.window, self.pieces)
        return pieces
