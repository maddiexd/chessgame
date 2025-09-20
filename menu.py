import tkinter as tk
from tkinter import IntVar, StringVar, messagebox, ttk
from startfile import startfile
from tkinter.constants import HORIZONTAL
window = tk.Tk()
window.eval('tk::PlaceWindow . center')

ttk.Style().theme_use('aqua')
window.geometry("800x600")  # initialising the window
from game import main as runGame # importing the main game
from replayGame import main as replayGame

window.title("Chess - Menu")

def menu(buttons = []):
    for button in buttons:
        button.destroy()
    def resumeGame():   # defining what is run when clicking resume game
        runGame(resume = True)

    def newGame():
        def runGameValid(fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", rotation = True, passPlay = False, perftDepth = -1, aiPlaysBlack = True, aiPlaysWhite = False, whiteTime = 0, blackTime = 0, resume = False, difficulty = 2):
            import functions
            fenCheck = False
            timeCheck = False

            if functions.checkFENs([fen]):  # checks for a valid FEN
                fenCheck = True
            else:
                messagebox.showinfo("Invalid", "The FEN entered into the layout is invalid")

            try:
                whiteTime = int(whiteTime)  # converts the times to integers
                blackTime = int(blackTime)
            except:
                pass    # don't if it's invalid
            if isinstance(whiteTime, int):  # do the range test if an integer
                if whiteTime <= 36000 and whiteTime >= 0:
                    timeCheck = True
            if not timeCheck:
                messagebox.showinfo("Invalid", "The time entered must be a positive integer with the requirements 0 <= x <= 36000")
            if fenCheck and timeCheck:
                runGame(fen, rotation, passPlay, perftDepth, aiPlaysBlack, aiPlaysWhite, whiteTime, blackTime, resume, difficulty)

        def select():
            pass
        def setBoxState(state, fen = ""):
            customBox.config(state = state)
            fenStr.set(fen)
        def setTimerState(state, timer = "0"):
            customTimerBox.config(state = state)
            timerStr.set(timer)
        clearMenu()
        # window.grid_columnconfigure(1, weight=1)
        # window.grid_columnconfigure(2, weight=1)
        clearList = []
        backButton = ttk.Button(window, command=lambda: menu(clearList), text="<--")
        backButton.config(padding=(4,4))
        backButton.grid(row=0, column = 0, sticky="nw")
        clearList.append(backButton)
        ## pick the team
        teamFrame = ttk.Frame()
        teamFrame.grid(row=1, column = 2, pady = 2, sticky="nsw")
        teamChoice = IntVar(value = 1)
        teamLabel = ttk.Label(teamFrame, text="Choose team (1 Player Only):")
        whiteChoice = ttk.Radiobutton(teamFrame, variable=teamChoice, text="White Team (Plays first)", value=1, command=select)
        blackChoice = ttk.Radiobutton(teamFrame, variable=teamChoice, text="Black Team (Plays second)", value=0, command=select)
        # whiteChoice.select()
        teamLabel.pack(anchor="w")
        whiteChoice.pack(anchor="w")
        blackChoice.pack(anchor="w")
        clearList.append(teamFrame)
        ## game style
        styleFrame = ttk.Frame()
        styleFrame.grid(row=2, column = 2, pady = 2, sticky="nsw")
        styleChoice = IntVar(value = 0)
        styleLabel = ttk.Label(styleFrame, text="Select Players:")
        stockfishChoice = ttk.Radiobutton(styleFrame, variable=styleChoice, text="1 Player (Stockfish AI)", value=0, command=select)
        passPlayChoice = ttk.Radiobutton(styleFrame, variable=styleChoice, text="2 Player (Pass and Play)", value=1, command=select)
        # stockfishChoice.select()
        styleLabel.pack(anchor="w")
        stockfishChoice.pack(anchor="w")
        passPlayChoice.pack(anchor="w")
        clearList.append(styleFrame)
        ## board layout
        layoutFrame= ttk.Frame()
        layoutFrame.grid(row=3, column = 2, pady = 2, sticky="nsw")
        layoutChoice = IntVar(value = 1)
        layoutLabel = ttk.Label(layoutFrame, text="Select Layout:")

        defaultChoice = ttk.Radiobutton(layoutFrame, variable=layoutChoice, text="Default", value=1, command=lambda: setBoxState("disabled", fen= "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"))
        customChoice = ttk.Radiobutton(layoutFrame, variable=layoutChoice, text="Custom", value = 0, command=lambda: setBoxState("normal"))
        fenStr = StringVar(value = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        customBox = ttk.Entry(layoutFrame, textvariable=fenStr, state="disabled")
        defaultChoice.invoke()
        layoutLabel.pack(anchor="w")
        defaultChoice.pack(anchor="w")
        customChoice.pack(anchor="w")
        customBox.pack(anchor="w")
        window.update_idletasks()
        clearList.append(layoutFrame)
        ## timer
        timerFrame= ttk.Frame()
        timerFrame.grid(row=4, column = 2, pady = 2, sticky="nsw")
        timerChoice = IntVar(value = 1)
        timerLabel = ttk.Label(layoutFrame, text="Select Timer:")
        defaultTimer = ttk.Radiobutton(layoutFrame, variable=timerChoice, text="Off", value=1, command=lambda: setTimerState("disabled", timer = "0"))
        customTimer = ttk.Radiobutton(layoutFrame, variable=timerChoice, text="Custom (in seconds)", value = 0, command=lambda: setTimerState("normal"))

        timerStr = StringVar(value = "0")
        customTimerBox = ttk.Entry(layoutFrame, textvariable=timerStr, state="disabled")
        # defaultTimer.invoke()
        timerLabel.pack(anchor="w")
        defaultTimer.pack(anchor="w")
        customTimer.pack(anchor="w")
        customTimerBox.pack(anchor="w")


        clearList.append(timerFrame)
        ## difficulty slider
        difficultyFrame = ttk.Frame()
        difficultyFrame.grid(row=5, column = 2, pady = 2, sticky="nsw")
        difficultySlider = ttk.Scale(difficultyFrame, from_= 0, to = 20, orient = HORIZONTAL, command = lambda val: difficultyLabel.config(text=f"Stockfish Difficulty: {round(float(val))}"))
        difficultyLabel = ttk.Label(difficultyFrame, text=f"Stockfish Difficulty: {difficultySlider.get()}")

        difficultyLabel.pack(anchor = "w")
        difficultySlider.pack(anchor = "w")
        clearList.append(difficultyFrame)
        ## play button
        playButton = ttk.Button(window, command=lambda: runGameValid(passPlay=(styleChoice.get() == True)
            , aiPlaysBlack=((teamChoice.get() == True) and not (styleChoice.get() == True))
            , aiPlaysWhite=((teamChoice.get() == False) and not (styleChoice.get() == True))
            , rotation=(teamChoice.get() == True)
            , blackTime = timerStr.get()
            , whiteTime = timerStr.get()
            , fen= fenStr.get()
            , difficulty = round(difficultySlider.get())), text="Play")

        playButton.config(padding=(8,2))
        playButton.grid(row=8, column = 2)
        clearList.append(playButton)
        window.update_idletasks()   # fix visual bug for macOS
        # runGame()

    def history():  # placeholders
        messagebox.showinfo("History", "History")

    def analyse():
        # menu()
        def exportPGN():
            import pickle
            with open("save.pkl", "rb") as save:    # open the save data
                fen, aiPlaysWhite, aiPlaysBlack, rotation, passPlay, whiteTime, blackTime, difficulty, fens, pgn = pickle.load(save)    # grab all the data
                saveFile = f"Exported save\nAI plays White: {aiPlaysWhite}\nAI plays Black: {aiPlaysBlack}\nWhite's clock in seconds: {whiteTime}\nBlack's clock in seconds: {blackTime}\nStockfish level: {difficulty}\nFEN List of all positions:\n{fens}\nAlgebraic:\n{pgn}"
                # format the data nicely
                save.close()
            with open("export.txt", "w") as export:
                # open and write to the file
                export.write(saveFile)
                # savedLabel = ttk.Label(text="Your file has been exported to ./export.txt", padding= (20, 2)) # display feedback
                messagebox.showinfo("Info", "Your file has been exported to ./export.txt")
                # savedLabel.grid(row=2, column = 1, sticky="nesw")

        def replayLastSave():
            import pickle
            with open("save.pkl", "rb") as save:
                fens  = pickle.load(save)[8]
                replayGame(fens)
        def replayFenTxt():
            import tkinter.filedialog
            filepath = tkinter.filedialog.askopenfilename()
            try:
                with open(filepath, "r") as imported:
                    fens  = imported.read().splitlines()
                    replayGame(fenList = fens)
            except Exception:
                # exceptionLabel = ttk.Label(text="invalid file", padding= (20, 2)) # display feedback
                messagebox.showinfo("Invalid File", "Invalid File")
                # exceptionLabel.grid(row=6, column = 1, sticky="nesw")
        def replayExported():
            import tkinter.filedialog
            filepath = tkinter.filedialog.askopenfilename()
            try:
                with open(filepath, "r") as imported:
                        fens  = eval(imported.readlines()[7])
                        replayGame(fenList = fens)
            except Exception:
                # exceptionLabel = ttk.Label(text="invalid file", padding= (20, 2)) # display feedback
                messagebox.showinfo("Invalid File", "Invalid File")
                # exceptionLabel.grid(row=6, column = 1, sticky="nesw")

        clearMenu()
        clearList = []
        backButton = ttk.Button(window, command=lambda: menu(clearList), text="<--")    # add the same back button
        backButton.config(padding=(4,4))
        backButton.grid(row=0, column = 0, sticky="nw")
        clearList.append(backButton)
        exportButton = ttk.Button(window, command=lambda: exportPGN(), text = "export pgn from last save", padding= (20, 2))    # add the export button
        exportButton.grid(row=1, column = 1, sticky="nesw")
        clearList.append(exportButton)

        replayCurrentSave = ttk.Button(window, command=lambda: replayLastSave(), text = "replay last save", padding= (20, 2))    # add the export button
        replayCurrentSave.grid(row=2, column = 1, sticky="nesw")
        clearList.append(replayCurrentSave)

        replayText = ttk.Button(window, command=lambda: replayFenTxt(), text = "import list of FENs", padding= (20, 2))    # add the export button
        replayText.grid(row=3, column = 1, sticky="nesw")
        clearList.append(replayText)

        replayExport = ttk.Button(window, command=lambda: replayExported(), text = "replay exported save", padding= (20, 2))    # add the export button
        replayExport.grid(row=4, column = 1, sticky="nesw")
        clearList.append(replayExport)
        # messagebox.showinfo("Options", "Options")

    def rules():
        # clearMenu()
        startfile("./Rules.pdf")
        # messagebox.showinfo("Rules", "Rules")




    def clearMenu():  # clearing the menu
        chessText.destroy()
        resumeButton.destroy()
        newGameButton.destroy()
        historyButton.destroy()
        rulesButton.destroy()
        # optionsButton.destroy()

    chessText = tk.Label(text="Chess", font=("", 50))   # adding text
    chessText.pack(pady=50)

    resumeButton = ttk.Button(window, command=resumeGame, text="Resume Game", width = 50) #adding buttons
    resumeButton.config(padding=(50, 2))
    resumeButton.pack(pady=2, padx=50)

    newGameButton = ttk.Button(window, command=newGame, text="New Game", width = 50)
    newGameButton.config(padding=(50, 2))
    newGameButton.pack(pady=2, padx=50)

    historyButton = ttk.Button(window, command=analyse, text="Analyse and export", width = 50)
    historyButton.config(padding=(50, 2))
    historyButton.pack(pady=2, padx=50)

    rulesButton = ttk.Button(window, command=rules, text="Rules", width = 50)
    rulesButton.config(padding=(50, 2))
    rulesButton.pack(pady=2, padx=50)

    # optionsButton = ttk.Button(window, command=options, text="Options", width = 50)
    # optionsButton.config(padding=(50, 2))
    # optionsButton.pack(pady=2, padx=50)

menu()
window.mainloop()
