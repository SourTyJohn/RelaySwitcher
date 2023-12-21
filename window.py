import PyQt5.QtWidgets as QW
from PyQt5.QtCore import QTimer, Qt
from PyQt5 import QtGui
import PyQt5.uic as uic

from Serial import SerialAPI, get_serial_ports
from CodeExecute import CodeAPI

from typing import Union

from easygui import filesavebox, fileopenbox
from utils import MessageWindow


PORT_READ_DELAY = 200
CODE_TICK_MS = 100


class HelpWindow(QW.QMainWindow):
    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi("templates/help.ui", self)
        self.setWindowTitle("RelaySwitcher: Help")
        self.show()
        self.setFocus()


class MainWindow(QW.QMainWindow):

    text_prog: QW.QTextEdit
    b_restart: QW.QPushButton
    b_pause: QW.QPushButton

    line_curr: int
    line_maxx: int
    timer_curr: int
    timer_maxx: int

    block_n: int

    paused: int

    def __init__(self):
        super().__init__()
        uic.loadUi("templates/main.ui", self)
        self.setWindowTitle("RelaySwitcher")

        self.__ports_window: Union[PortsWindow, None] = None
        self.openPortsWindow()

        self.timer = QTimer(self)
        self.timer.setInterval(CODE_TICK_MS)
        self.timer.timeout.connect(self.tick)
        self.timer.start()

        self.state = [0, 0, 0, 0, 0, 0, 0, 0]

        self.buttons_r = [self.b_r1, self.b_r2, self.b_r3, self.b_r4, self.b_r5, self.b_r6, self.b_r7, self.b_r8]
        self.b_r1.clicked.connect(lambda: self.press_b([0, ]))
        self.b_r2.clicked.connect(lambda: self.press_b([1, ]))
        self.b_r3.clicked.connect(lambda: self.press_b([2, ]))
        self.b_r4.clicked.connect(lambda: self.press_b([3, ]))
        self.b_r5.clicked.connect(lambda: self.press_b([4, ]))
        self.b_r6.clicked.connect(lambda: self.press_b([5, ]))
        self.b_r7.clicked.connect(lambda: self.press_b([6, ]))
        self.b_r8.clicked.connect(lambda: self.press_b([7, ]))

        self.buttons_s = [self.b_s1, self.b_s2, self.b_s3, self.b_s4]
        self.b_s1.clicked.connect(lambda: self.press_b([0, 1]))
        self.b_s2.clicked.connect(lambda: self.press_b([2, 3]))
        self.b_s3.clicked.connect(lambda: self.press_b([4, 5]))
        self.b_s4.clicked.connect(lambda: self.press_b([6, 7]))

        self.program = []
        self.paused = 1
        self.pause_code(1)
        self.codeAPI = CodeAPI()
        self.restart_code()

        self.b_restart.clicked.connect( lambda: self.restart_code(paused=0) )
        self.b_pause.clicked.connect( lambda: self.pause_code() )

        self.menu_file.addAction("Открыть", self.file_open)
        self.menu_file.addAction("Сохранить", self.file_save)

        self.menu_port.addAction("Подключиться", self.openPortsWindow)
        self.menu_help.addAction("Показать", self.open_help_window)

    def file_save(self):
        file_path = filesavebox("Сохранить как", filetypes="*.txt",)
        if not file_path: return
        with open(file_path, mode="w") as file:
            file.write(self.file_view_table.toPlainText())

    def file_open(self):
        file_path = fileopenbox("Открыть", filetypes="*.txt",)
        if not file_path: return
        with open(file_path, mode="r") as file:
            self.text_prog.setText( file.read() )

    def open_help_window(self):
        HelpWindow(self, )

    def tick(self):
        line_n, rtn_code = self.codeAPI.step(CODE_TICK_MS, self.paused)

        if rtn_code not in ("PAUSED", "FINISHED"):
            self.text_prog.setText(
                '\n'.join( self.program[:line_n - 1]) +
                '\n >>' + self.program[line_n - 1] + '\n' +
                '\n'.join( self.program[line_n:])
            )
        if rtn_code == 'FINISHED':
            self.pause_code(1)
            self.text_prog.setText( '\n'.join( self.program) )

        elif rtn_code[0] == 's':
            state = list(rtn_code[1:])
            self.state = [ 1 if str(x + 1) in state else 0 for x in range(len( self.state )) ]
            self.check_states()

        elif rtn_code == '0':
            self.state = [0, ] * len(self.state)
            self.check_states()

    def openPortsWindow(self):
        if self.__ports_window:
            self.__ports_window.close()
        self.__ports_window = PortsWindow(self, )
        self.__ports_window.show()
        self.__ports_window.setFocus()

    def sendCommand(self):
        line = f"s{''.join( [str(i + 1) if x else '' for i, x in enumerate(self.state)] )}"
        if line == 's':
            line = '0'
        SerialAPI.sendLine(line + '\n\r')

    def press_b(self, states: list):
        if len(states) == 2 and self.state[ states[0] ] != self.state[ states[1] ]:
            self.state[ states[0] ] = 0
            self.state[ states[1] ] = 0

        for s in states:
            self.state[s] = abs( self.state[s] - 1 )
        self.check_states()
        self.sendCommand()

    def check_states(self):
        for x in range( len(self.state) // 2 ):
            k = 0
            if self.state[x * 2]:
                self.buttons_r[x * 2].setStyleSheet("background-color: green")
                k += 1
            else:
                self.buttons_r[x * 2].setStyleSheet("background-color: grey")

            if self.state[x * 2 + 1]:
                self.buttons_r[x * 2 + 1].setStyleSheet("background-color: green")
                k += 1
            else:
                self.buttons_r[x * 2 + 1].setStyleSheet("background-color: grey")

            if k == 2:
                self.buttons_s[x].setStyleSheet("background-color: green")
            else:
                self.buttons_s[x].setStyleSheet("background-color: grey")

    def restart_code(self, paused=1):
        self.program = self.text_prog.toPlainText().split('\n')
        for i, line in enumerate( self.program ):
            self.program[i] = line.replace(' >>', '')

        self.codeAPI.compile( self.program )
        self.pause_code(1)

        self.line_curr = 0
        self.line_maxx = 0
        self.timer_curr = 0
        self.timer_maxx = 0
        self.paused = paused
        if paused == 0 and self.text_prog.toPlainText():
            self.pause_code(0)

    def pause_code(self, forced=-1):
        if forced == -1:
            self.paused = abs(self.paused - 1)
        else:
            self.paused = forced

        if self.paused:
            self.b_pause.setStyleSheet("background-color: grey")
            self.b_pause.setText("PAUSED")
            self.text_prog.setReadOnly( False )
        else:
            self.b_pause.setStyleSheet("background-color: white")
            self.b_pause.setText("RUNNING")
            self.text_prog.setReadOnly( True )

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        match a0.key():
            case Qt.Key_F1:
                self.press_b([0, 1])
            case Qt.Key_F2:
                self.press_b([2, 3])
            case Qt.Key_F3:
                self.press_b([4, 5])
            case Qt.Key_F4:
                self.press_b([6, 7])


class PortsWindow(QW.QMainWindow):
    def __init__(self, _parent):
        super().__init__(parent=_parent)
        uic.loadUi("templates/port.ui", self)
        self.ports_update()
        self.b_connect.clicked.connect(self.connect)
        self.b_ports_update.clicked.connect(self.ports_update)

    def ports_update(self):
        self.portSelect.clear()
        self.portSelect.addItems(get_serial_ports())

    def connect(self):
        self.parent().timer.stop()

        if not self.portSelect.currentText():
            MessageWindow(self, "Не указан порт")
            return

        err_code = SerialAPI.usePort( self.portSelect.currentText() )

        if err_code == 0:
            self.b_connect.setStyleSheet("background-color: green")
            self.parent().timer.start()
        else:
            self.b_connect.setStyleSheet("background-color: red")
            MessageWindow(self, "Не удалось подключиться к порту")
