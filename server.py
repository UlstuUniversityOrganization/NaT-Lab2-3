import socket
import threading
import sys
import struct
import math
from PyQt5 import QtWidgets
from PyQt5 import QtGui
import ast
# from src.MD4 import MD4
from src.SHA256 import SHA256
from src.generators.bbs_generator import BbsGenerator
# from src.generators.fips_generator import FIPSGenerator

HOST = '127.0.0.1'
PORT = 12344


def lcg(a, b, m, seed, length):
    sequence = []
    x = seed
    for _ in range(length):
        x = (a * x + b) % m
        sequence.append(x % 256)
    return sequence


def encrypt_message(message, password):
    hashed_password = SHA256().to_hash(password)
    generator = BbsGenerator(int(hashed_password, 16))
    encrypted_message = "".join(hex(ord(c) ^ (generator.rand_value() % 256))[2:].zfill(2) for c in message)
    # encrypted_message = "TEEEST"
    return encrypted_message

def decrypt_message(message, password):
    hashed_password = SHA256().to_hash(password)
    generator = BbsGenerator(int(hashed_password, 16))
    decrypted_message = "".join(chr(int(message[i*2:i*2+2], 16) ^ (generator.rand_value() % 256)) for i in range(len(message)//2))
    return decrypted_message


class ServerApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.start()

    def initUI(self):
        self.setWindowTitle('Сервер')
        self.setGeometry(300, 300, 600, 400)

        self.output_area = QtWidgets.QTextEdit(self)
        self.output_area.setReadOnly(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.output_area)
        self.setLayout(layout)

    def log_message(self, message):
        self.output_area.append(message)

    def handle_client(self, conn, addr):
        self.log_message(f"Подключен клиент {addr}")
        with conn:
            while True:
                data = conn.recv(1024).decode().strip()
                if not data:
                    break

                if data.endswith(chr(0x10)):
                    data = data[:-1]

                self.log_message(f"Получено: {data}")
                command = data.split()[0].lower()

                if command == "hello":
                    variant = data.split()[1]
                    response = f"hello variant {variant}"
                elif command == "bye":
                    variant = data.split()[1]
                    response = f"bye variant {variant}"
                    conn.sendall(response.encode())
                    break
                elif command == "encrypt":
                    try:
                        parts = data.split()

                        password = parts[1]
                        message = " ".join(parts[2:])

                        response = encrypt_message(message, password)
                    except Exception:
                        response = "Неверные параметры"
                elif command == "decrypt":
                    try:
                        parts = data.split()

                        password = parts[1]
                        message = " ".join(parts[2:])

                        response = decrypt_message(message, password)
                    except Exception:
                        response = "Неверные параметры"
                else:
                    response = "Неизвестная команда"

                conn.sendall(response.encode('utf-8'))

            self.log_message(f"Отключен клиент {addr}")

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            self.log_message(f"Сервер запущен на {HOST}:{PORT}")
            while True:
                conn, addr = s.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.start()


def set_dark_palette(app):
    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(45, 45, 45))
    dark_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(208, 208, 208))
    dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(18, 18, 18))
    dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(45, 45, 45))
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(208, 208, 208))
    dark_palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(208, 208, 208))
    dark_palette.setColor(QtGui.QPalette.Text, QtGui.QColor(208, 208, 208))
    dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(45, 45, 45))
    dark_palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(208, 208, 208))
    dark_palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 0, 0))
    dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(35, 35, 35))

    app.setPalette(dark_palette)

    dark_qss = """
    QWidget {
        background-color: #000000;
        color: #ffffff;
    }

    QLineEdit, QTextEdit {
        background-color: #000000;
        color: #ffffff;
        border: 1px solid #666666;
    }

    QTableWidget {
        background-color: #000000;
        color: #ffffff;
        gridline-color: #444444;
    }

    QHeaderView::section {
        background-color: #222222;
        color: #ffffff;
        border: 1px solid #666666;
    }

    QPushButton {
        background-color: #000000;
        color: #ffffff;
        border: 1px solid #666666;
        padding: 5px;
    }

    QPushButton:hover {
        background-color: #44444;
    }

    QTabWidget::pane { /* Border and background for tab area */
        background: #2e2e2e;
        border: 1px solid #444444;
    }

    QTabBar::tab {
        background: #000000;
        color: #ffffff;
        padding: 5px;
    }

    QTabBar::tab:selected {
        background: #222222;
        color: #ffffff;
    }
    """
    app.setStyleSheet(dark_qss)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    set_dark_palette(app)
    server = ServerApp()
    server.show()
    sys.exit(app.exec_())
