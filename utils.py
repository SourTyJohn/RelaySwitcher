import PyQt5.QtWidgets as QW
from PyQt5.QtGui import QFont


class MessageWindow(QW.QMainWindow):

    def __init__(self, parent: QW.QMainWindow, message):
        super(MessageWindow, self).__init__(parent)
        self.label = QW.QLabel(parent=self, text=message)
        self.label.setFont( QFont("MS Sans Serif", pointSize=12) )
        self.setCentralWidget(self.label)
        self.setWindowTitle("Сообщение")
        self.setGeometry(parent.geometry().x() + 40, parent.geometry().y() + 40, 300, 50)
        self.show()
        self.setFocus()
