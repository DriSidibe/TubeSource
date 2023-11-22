import sys
from PyQt5.QtWidgets import *


def window():
    # create pyqt5 app
    app = QApplication(sys.argv)
    w = QWidget()

    # create buttons

    # b1- Information button
    b1 = QPushButton(w)
    b1.setText("Information")
    b1.move(45, 50)

    # b2- Warning button
    b2 = QPushButton(w)
    b2.setText("Warning")
    b2.move(150, 50)

    # b3- Question button
    b3 = QPushButton(w)
    b3.setText("Question")
    b3.move(50, 150)

    # b4- Critical button
    b4 = QPushButton(w)
    b4.setText("Critical")
    b4.move(150, 150)

    # declaring command when button clicked
    b1.clicked.connect(show_info_messagebox)
    b2.clicked.connect(show_warning_messagebox)
    b3.clicked.connect(show_question_messagebox)
    b4.clicked.connect(show_critical_messagebox)

    # setting title of the window
    w.setWindowTitle("PyQt MessageBox")

    # showing all the widgets
    w.show()

    # start the app
    sys.exit(app.exec_())


def show_info_messagebox(message="Warning messsage"):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)

    # setting message for Message Box
    msg.setText(message)

    # setting Message box window title
    msg.setWindowTitle("Information")

    # declaring buttons on Message Box
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    # start the app
    retval = msg.exec_()


def show_warning_messagebox():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)

    # setting message for Message Box
    msg.setText("Warning")

    # setting Message box window title
    msg.setWindowTitle("Warning")

    # declaring buttons on Message Box
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    # start the app
    retval = msg.exec_()


def show_question_messagebox():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Question)

    # setting message for Message Box
    msg.setText("Question")

    # setting Message box window title
    msg.setWindowTitle("Question")

    # declaring buttons on Message Box
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    # start the app
    retval = msg.exec_()


def show_critical_messagebox(message="Error messsage"):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)

    # setting message for Message Box
    msg.setText(message)

    # setting Message box window title
    msg.setWindowTitle("Error")

    # declaring buttons on Message Box
    msg.setStandardButtons(QMessageBox.Ok)

    # start the app
    retval = msg.exec_()

class CriticalMessageBox(QMessageBox):
    def __init__(self, message):
        super().__init__()
        self.setText(message)
        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    def show(self):
        return super().exec_()
    
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Quit', 'Are you sure you want to quit?',
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()

if __name__ == '__main__':
    window()