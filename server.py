

from functools import partial
import threading
import socket
import pickle
import pyperclip


class Server():
    def __init__(self, gui):
        super().__init__()
        self.dataReceive = ""
        self.connection = None
        self.gui = gui
        self.board = None
        self.player1 = None
        self.player2 = None
        self.currentBtn = None
        self.ipRoom = ""
        self.name = ""

    def makeHost(self):
        try:
            self.name = "server"
            HOST = socket.gethostbyname(
                socket.gethostname())  # Láy  lập địa chỉ
            print("Make host.........." + HOST)
            self.gui.notify("Notification", "IP room: "+str(HOST))
            self.gui.labelIpRoom.config(text="IP Room: "+str(HOST))
            pyperclip.copy(HOST)
            self.ipRoom = HOST
            PORT = 8000  # Thiết lập port lắng nghe
            # cấu hình kết nối
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((HOST, PORT))  # lắng nghe
            s.listen(1)  # thiết lập tối ta 1 kết nối đồng thời
            self.connection, addr = s.accept()  # chấp nhận kết nối và trả về thông số
            t2 = threading.Thread(target=self.server, args=(addr, s))
            t2.start()
            self.player1 = self.gui.player1_name.get()
            self.gui.startGame("host")
        except:
            self.gui.notify("Error", "Can not create room")
            return False

    def joinHost(self, ip):
        try:
            self.name = "client"
            print("client connect ...............")
            HOST = ip  # Cấu hình địa chỉ server
            PORT = 8000              # Cấu hình Port sử dụng
            self.connection = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)  # Cấu hình socket
            # tiến hành kết nối đến server
            self.connection.connect((HOST, PORT))
            self.gui.notify("Connected room: ", str(HOST))
            print("Connected room: ", str(HOST))
            t1 = threading.Thread(target=self.client)  # tạo luồng chạy client
            t1.start()
            self.player2 = self.gui.player1_name.get()
            self.gui.startGame("client")
            return True
        except:
            self.gui.notify("Error", "Can not connect to room")
            return False

    def client(self):
        while True:
            self.dataReceive = self.connection.recv(
                1024).decode()  # Đọc dữ liệu server trả về
            if (self.dataReceive != ""):
                friend = self.dataReceive.split("|")[0]
                action = self.dataReceive.split("|")[1]
                btn = self.dataReceive.split("|")[4]
                row = int(self.dataReceive.split("|")[2])
                col = int(self.dataReceive.split("|")[3])
                print(self.dataReceive)
                # print("client: ", action, friend, btn, row, col)
                if (action == "hit" and friend == "server"):
                    self.gui.fillWitPos(row, col)
                    self.gui.enable()
                    print("xsdsd")

            self.dataReceive = ""
            self.currentBtn = None

    def server(self, addr, s):
        try:
            print('Connected by', addr)
            while True:
                self.dataReceive = self.connection.recv(1024).decode()
                if (self.dataReceive != ""):
                    friend = self.dataReceive.split("|")[0]
                    action = self.dataReceive.split("|")[1]
                    row = int(self.dataReceive.split("|")[2])
                    col = int(self.dataReceive.split("|")[3])
                    btn = self.dataReceive.split("|")[4]
                    # print("server: ", action, friend, btn, row, col)
                    print(self.dataReceive, self.board)
                    if (action == "hit" and friend == "client"):
                        self.gui.fillWitPos(row, col)
                        self.gui.enable()
                        print("xxxxx")
                self.dataReceive = ""
                self.currentBtn = None
        finally:
            s.close()  # đóng socket

    def sendData(self, data, btn):
        # print(data, btn)
        # self.currentBtn = btn
        # Gửi dữ liệu lên server`
        # data = str("{}|".format(self.name) + data)
        # print(data)
        self.connection.sendall(str("{}|".format(self.name) + data).encode())
