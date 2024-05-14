from itertools import cycle
import pprint
import time
import tkinter as tk
from tkinter import Label, font
from tkinter import messagebox
from typing import NamedTuple, Tuple
from server import Server


BOARD_SIZE = 20


class Player:
    def __init__(self, name, symbol, color):
        self.name = name
        self.symbol = symbol
        self.color = color


class Move(NamedTuple):
    row: int
    col: int
    player: Player


class Menu:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Caro Game")
        self.window.geometry("200x200")
        self.player1_name = tk.StringVar()
        self.player2_name = tk.StringVar()
        self.ipRoom = None
        self.board = None
        self.inputIp = tk.StringVar()

        self.labelIpRoom = tk.Label(self.window, text="IP Room: {ip} ".format(
            ip=self.ipRoom))
        self.labelIpRoom.pack()

        tk.Button(self.window, text="Create a room",
                  command=self.createRoom).pack()
        tk.Label(self.window, text="").pack()
        tk.Label(self.window, text="------- OR -------").pack()
        tk.Label(self.window, text="IP: ").pack()
        tk.Entry(self.window, textvariable=self.inputIp).pack()
        tk.Button(self.window, text="Connect",
                  command=self.connectRoom).pack()
        self.server = Server(self)
        # self.window.mainloop()
        self.window.mainloop()

    def notify(self, title, msg):
        messagebox.showinfo(str(title), str(msg))

    def createRoom(self):

        status = self.server.makeHost()

    def connectRoom(self):

        status = self.server.joinHost(self.inputIp.get())

    def startGame(self, type):
        first = Player(self.player1_name.get(), "X", "red")
        second = Player("Client", "O", "blue")
        game = Game(first, second)
        self.board = Board(game, self.server)

        self.window.withdraw()

        self.board.start()

    def enable(self):
        self.board.game.can = True

    def fillWitPos(self, row, col):

        btn = self.board.get_key_by_value(self.board.cells, (row, col))
        move = Move(row, col, self.board.game.current)
        self.board.game.processMove(move)
        self.board.updateButton(btn)
        self.board.game.switch()
        self.board.updateInfo()
        if (self.board.game.winner != None):
            for button in self.board.cells.keys():
                button.config(state=tk.DISABLED)

    def again(self):
        for button, coordinates in self.board.cells.items():
            if coordinates in self.board.game.winning_path:
                button.config(bg="white")
        self.board.game.reset()
        self.board.game.can = True
        for button in self.board.cells.keys():
            button.config(text="")
            button.config(fg="black")
        for button in self.board.cells.keys():
            button.config(state=tk.NORMAL)


class Game:
    def __init__(self, first: Player, second: Player):
        self.players = cycle([first, second])
        # self.first = Player(first.name, first.symbol)
        # self.second = Player(second.name, second.symbol)
        self.current = next(self.players)
        self.winner = None
        self.can = True
        self.winning_path = []
        # self.current_moves = []
        self.current_moves = [
            [Move(row, col, None) for col in range(BOARD_SIZE)]
            for row in range(BOARD_SIZE)
        ]

    def processMove(self, move: Move):
        row, col = move.row, move.col
        self.current_moves[row][col] = move
        # check winning here
        if (self.check_winning()):
            print("Winner is ", self.winner.name)

    def switch(self):
        self.current = next(self.players)

    def isValidMove(self, move: Move):
        if (self.winner == None):
            if (self.can == True):

                row, col = move.row, move.col
                return self.current_moves[row][col].player == None
            else:
                messagebox.showinfo("Notification", "Not your turn")
                return False

        return False

    def check_winning(self, condition=5):

        for row in self.current_moves:
            for i in range(BOARD_SIZE - condition + 1):
                if len(set(move.player for move in row[i:i+condition])) == 1 and row[i].player is not None:
                    self.winner = row[i].player
                    self.winning_path = [(move.row, move.col)
                                         for move in row[i:i+condition]]
                    return True
        for j in range(BOARD_SIZE):
            for i in range(BOARD_SIZE - condition + 1):
                if len(set(self.current_moves[x][j].player for x in range(i, i+condition))) == 1 and self.current_moves[i][j].player is not None:
                    self.winner = self.current_moves[i][j].player
                    self.winning_path = [(x, j) for x in range(i, i+condition)]
                    return True
        # check diagonals from top-left to bottom-right
        for i in range(BOARD_SIZE - condition + 1):
            for j in range(BOARD_SIZE - condition + 1):
                if len(set(self.current_moves[i+x][j+x].player for x in range(condition))) == 1 and self.current_moves[i][j].player is not None:
                    self.winner = self.current_moves[i][j].player
                    self.winning_path = [(i+x, j+x) for x in range(condition)]

                    return True
        # check diagonals from top-right to bottom-left
        for i in range(BOARD_SIZE - condition + 1):
            for j in range(condition - 1, BOARD_SIZE):
                if len(set(self.current_moves[i+x][j-x].player for x in range(condition))) == 1 and self.current_moves[i][j].player is not None:
                    self.winner = self.current_moves[i][j].player
                    self.winning_path = [(i+x, j-x) for x in range(condition)]
                    return True
        return False

    def reset(self):
        for row, row_content in enumerate(self.current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col, None)
        self.winning_path = []
        self.winner = None


class Board:
    def __init__(self, game: Game, server: Server, size=BOARD_SIZE):
        print("Caro Game")
        self.root = tk.Tk()
        self.size = size
        self.game = game
        self.server = server
        self.cells = {}
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        self.root.title("Caro Game")
        self.root.geometry("520x700")
        # self.root.geometry("620x660")
        self.root.resizable(False, False)
        self.create_menu()

    def quit(self):
        self.root.destroy()

        # quit()
    def create_menu(self):
        menu_bar = tk.Menu(master=self.root)
        self.root.config(menu=menu_bar)
        menu = tk.Menu(master=menu_bar)
        menu.add_command(label="Play Again", command=self.resetBoard)
        menu.add_separator()
        menu_bar.add_cascade(label="Menu", menu=menu)

    def create_widgets(self):
        self.canvas = tk.Canvas(self.root, bg="white", width=520, height=560)
        labelCurrent = Label(self.root, text="Current Symbol: {symbol}".format(
            symbol=self.game.current.symbol))
        labelWinner = Label(self.root, text="Winner: {winner}".format(
            winner=self.game.winner.symbol if self.game.winner != None else "None"))
        labelCurrent.pack()
        labelWinner.pack()
        self.labelCurrent = labelCurrent
        self.labelWinner = labelWinner
        self.canvas.pack(side=tk.LEFT)

        self.create_board()

    def create_board(self):
        self.board = []
        for i in range(self.size):
            row = []
            for j in range(self.size):

                cell = tk.Button(self.canvas, text="", width=2,
                                 height=1, font=font.Font(size=12))
                cell.grid(row=i, column=j)
                cell.bind("<Button-1>", self.fill)
                row.append(cell)
                self.cells[cell] = (i, j)

    def get_key_by_value(self, dictionary: dict, tup: tuple):
        for key, value in dictionary.items():
            if value == tup:
                return key
        return None

    def fill(self, event):
        btn = event.widget
        row, col = self.cells[btn]
        move = Move(row, col, self.game.current)
        if (self.game.isValidMove(move) == True):
            self.game.processMove(move)
            self.updateButton(btn)
            self.server.sendData("{}|{}|{}|".format("hit", row, col))
            self.game.switch()
            self.game.can = False
            self.updateInfo()
            if (self.game.winner != None):
                for button in self.cells.keys():
                    button.config(state=tk.DISABLED)

        else:
            return False

    def updateButton(self, btn):
        btn.config(text=self.game.current.symbol)
        btn.config(fg=self.game.current.color)

    def updateInfo(self):
        if (self.game.winner != None):
            for button, coordinates in self.cells.items():
                if coordinates in self.game.winning_path:
                    button.config(bg=self.game.winner.color)
            # self.game.current = None
            self.labelWinner.config(
                text="Winner: {name}".format(name=self.game.winner.symbol))
        self.labelCurrent.config(text="Current Symbol: {symbol}".format(
            symbol=self.game.current.symbol if self.game.current != None else "None"))

    def resetBoard(self):
        for button, coordinates in self.cells.items():
            if coordinates in self.game.winning_path:
                button.config(bg="white")
        self.game.reset()
        self.game.can = True
        for button in self.cells.keys():
            button.config(text="")
            button.config(fg="black")
        for button in self.cells.keys():
            button.config(state=tk.NORMAL)
        self.server.sendData("again")

    def start(self):
        self.create_widgets()
        self.root.mainloop()


def main():
    Menu()


main()
