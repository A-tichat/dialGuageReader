import sys
import serial
import glob
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from datetime import datetime as Date
import pandas as pd
import threading as thread


class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi("mainQt.ui", self)
        self.ser = serial.Serial()
        self.timerSerial = QtCore.QTimer()
        self.timerSerial.timeout.connect(self.timerSerialTick)
        self.scanBtn.clicked.connect(self.scanClick)
        self.connectBtn.clicked.connect(self.connectClick)
        self.disconnectBtn.clicked.connect(self.disconnectClick)
        self.comboPort.currentTextChanged.connect(self.comboPortChange)
        self.comboBaudRate.currentTextChanged.connect(self.comboBaudRateChange)
        self.startBtn.clicked.connect(self.startClick)
        self.stopBtn.clicked.connect(self.stopClick)
        self.clearBtn.clicked.connect(self.clearClick)
        self.exportBtn.clicked.connect(self.exportClick)
        self.rowCount = 1
        self.isRecord = False
        self.csv_log = pd.DataFrame(columns=['No', 'Value', 'Time', 'Date'])
        self.reading_event = thread.Event()
        self.reading_thread = thread.Thread(
            target=self.reading, daemon=True)

    def reading(self):
        while not self.reading_event.is_set():
            raw_reading = self.ser.read()
            print(raw_reading)

    def timerSerialTick(self):
        if (self.ser.isOpen()):
            tData = self.ser.read(self.ser.inWaiting()
                                  ).decode('utf-8').rstrip()
            rowPosition = self.tableData.rowCount()
            if (self.isBegin):
                self.tableData.setRowCount(0)
                rowPosition = 0
            self.tableData.insertRow(rowPosition)
            date = Date.now()
            self.tableData.setItem(
                rowPosition, 0, QtWidgets.QTableWidgetItem(str(tData)))
            self.tableData.setItem(
                rowPosition, 1, QtWidgets.QTableWidgetItem(date.strftime('%H:%M:%S')))
            self.tableData.setItem(
                rowPosition, 2, QtWidgets.QTableWidgetItem(date.strftime('%d/%m/%Y')))
            self.tableData.scrollToBottom()
            self.isBegin = False
            if (self.isRecord):
                self.csv_log.loc[self.rowCount] = [
                    self.rowCount, tData, date.strftime('%H:%M:%S'), date.strftime('%d/%m/%Y')]
                self.rowCount += 1

    def scanClick(self):
        portlist = self.getComPort()
        if (len(portlist) > 0):
            self.comboPort.addItems(portlist)
        else:
            self.errorPopup('Warning !!!', 'Com port not detected')

    def connectClick(self):
        # print('comport',self.comboPort.currentText())
        # print('baudrate',self.comboBaudRate.currentText())
        self.iconStatus.setPixmap(QtGui.QPixmap('./resource/Green.png'))
        self.ser.open()
        self.connectBtn.setEnabled(False)
        while not self.ser.isOpen():
            pass
        self.labelStatus.setText('Status : Connected')
        self.timerSerial.start(1000)
        self.scanBtn.setEnabled(False)
        self.disconnectBtn.setEnabled(True)
        self.startBtn.setEnabled(True)
        self.isBegin = True

    def disconnectClick(self):
        self.iconStatus.setPixmap(QtGui.QPixmap('./resource/Red.png'))
        self.disconnectBtn.setEnabled(False)
        self.ser.close()
        while self.ser.isOpen():
            pass
        self.labelStatus.setText('Status : Disconnect')
        self.connectBtn.setEnabled(True)
        self.scanBtn.setEnabled(True)
        self.startBtn.setEnabled(False)
        self.timerSerial.stop()
        self.isBegin = True

    def comboPortChange(self):
        self.ser.port = self.comboPort.currentText()
        self.comboBaudRate.clear()
        self.comboBaudRate.addItems(['300', '600', '1200', '2400', '4800', '9600',
                                     '14400', '19200', '28800', '31250', '38400', '57600', '115200'])
        self.comboBaudRate.setCurrentIndex(5)
        self.connectBtn.setEnabled(True)

    def comboBaudRateChange(self):
        self.ser.baudrate = int(self.comboBaudRate.currentText())

    def startClick(self):
        self.recordIconStatus.setPixmap(QtGui.QPixmap('./resource/Green.png'))
        self.startBtn.setEnabled(False)
        self.stopBtn.setEnabled(True)
        self.isRecord = True

    def stopClick(self):
        self.recordIconStatus.setPixmap(QtGui.QPixmap('./resource/Red.png'))
        self.startBtn.setEnabled(True)
        self.stopBtn.setEnabled(False)
        self.isRecord = False

    def clearClick(self):
        self.isBegin = True
        self.tableData.setRowCount(0)
        self.tableData.insertRow(0)

    def exportClick(self):
        dialog = QtWidgets.QFileDialog(
            self, 'Choose location to save csv file')
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            RESULT_DIRECTORY = dialog.selectedFiles()[0]
            self.csv_log.to_csv(
                RESULT_DIRECTORY+'/arduino_data.csv', index=False, header=True)

    def errorPopup(self, title, text):
        error_dialog = QtWidgets.QMessageBox()
        error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
        error_dialog.setWindowTitle(title)
        error_dialog.setText(text)
        error_dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)

        error_dialog.exec_()

    def getComPort(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            self.errorPopup('Error !!!', 'Unsupported platform')
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
