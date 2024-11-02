import os
import sys
import socket
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtWidgets import QFileDialog, QMessageBox

HOST = '127.0.0.1'
PORT = 12344


class ClientApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))

    def initUI(self):
        self.setWindowTitle('Client')
        self.setGeometry(300, 300, 600, 400)

        self.command_input = QtWidgets.QLineEdit(self)
        self.command_input.setPlaceholderText("Введите команду...")

        self.send_button = QtWidgets.QPushButton("Отправить", self)
        self.send_button.clicked.connect(self.send_command)

        self.file_button = QtWidgets.QPushButton("Выбрать файл", self)
        self.file_button.clicked.connect(self.select_file)

        self.path_input = QtWidgets.QLineEdit(self)
        self.path_input.setPlaceholderText("Путь до файла...")

        self.output_area = QtWidgets.QTextEdit(self)
        self.output_area.setReadOnly(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.command_input)
        layout.addWidget(self.send_button)
        layout.addWidget(self.file_button)
        layout.addWidget(self.path_input)
        layout.addWidget(self.output_area)

        self.setLayout(layout)

        self.selected_file = None

    def select_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "", options=options)
        self.path_input.setText(file_name)
        if file_name:
            self.selected_file = file_name
            self.output_area.append(f"Выбран файл: {self.selected_file}")

    def clear_file(self):
        self.selected_file = None
        self.output_area.append("Файл очищен.")

    def send_command(self):
        command = self.command_input.text()
        command_type = command.lower().split()[0]
        if (command_type == "encrypt" or command_type == "decrypt") and len(command.split()) == 3 and command.split()[2] == "[file]":
            password = command.split()[1]
            
            path = self.path_input.text()
            if path is None or len(path) == 0:
                QMessageBox.warning(self, "Ошибка", "Выберите файл для отправки.")
                return
            
            with open(path, "r") as f:
                text_data = f.read()
            
            command = f"{command_type} {password} {text_data}"
        elif (command_type == "encrypt" or command_type == "decrypt") and len(command.split()) > 2:
            password = command.split()[1]
            text_data = " ".join(command.split()[2:])
            command = f"{command_type} {password} {text_data}"
        elif command_type == "encrypt" or command_type == "decrypt":
            QMessageBox.warning(self, "Ошибка", "Неверные аргументы.")
            return

        command += chr(0x10)

        self.s.sendall(command.encode())
        response = self.s.recv(1024).decode().strip()

        if command_type == "bye":
            self.s.close()
            QtWidgets.qApp.quit()

        if command_type == "encrypt" or command_type == "decrypt":
            if not all(c.isprintable() for c in response):
                self.output_area.append(f"Ответ сервера: не удалось расшифровать")
                return

            local_path = os.path.join(os.getcwd(), 'lab2') + f".{command_type}"
            with open(local_path, 'w') as f:
                f.write(response)
            self.output_area.append(f"Ответ сервера: {str(response)}")
        else:
            self.output_area.append(f"Ответ сервера: {response.encode('utf-8', errors='replace')}")


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
    client = ClientApp()
    client.show()
    sys.exit(app.exec_())
