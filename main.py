import re
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvas
import matplotlib.pyplot as plt
import sys
import numpy as np
import serial
import glob
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from datetime import datetime as Date

import matplotlib
matplotlib.use('QT5Agg')


class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi("resource/mainQt.ui", self)
        # test data
        self.isFill = False
        self.angles = np.array([])
        self.values = np.array([])
        self.fig, self.ax1 = plt.subplots()
        self.ax1.plot(self.angles, self.values)
        # plot
        self.canvas = FigureCanvas(self.fig)
        self.lay = QtWidgets.QVBoxLayout(self.content_plot)
        self.lay.addWidget(self.canvas)
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
        self.inputPd.returnPressed.connect(self.insertPicthDiameter)
        self.inputGearTeeth.returnPressed.connect(self.insertGearTeeth)
        self.inputFi.returnPressed.connect(self.insertRadialComposite)
        self.input_fi.returnPressed.connect(self.insertToothToTooth)
        self.inputFr.returnPressed.connect(self.insertRunoutError)
        self.setToleranceValue()

    def setToleranceValue(self, maximun=0.00, minimun=9999.00, summary=0.00):
        self.maximumData = maximun
        self.minimumData = minimun
        self.sumData = summary

    def insertPicthDiameter(self):
        if (checkFloat(self.inputPd.text())):
            self.pdValue = float(self.inputPd.text())
            self.pdResult.setText(str(self.pdValue))
            self.inputPd.clear()

    def insertGearTeeth(self):
        if (checkFloat(self.inputGearTeeth.text())):
            self.gearTeethValue = float(self.inputGearTeeth.text())
            self.gearTeethResult.setText(str(self.gearTeethValue))
            self.inputGearTeeth.clear()

    def insertRadialComposite(self):
        if (checkFloat(self.inputFi.text())):
            self.fiValue = float(self.inputFi.text())
            self.fiRef.setText(str(self.fiValue))
            self.inputFi.clear()

    def insertToothToTooth(self):
        if (checkFloat(self.input_fi.text())):
            self.fiTotValue = float(self.input_fi.text())
            self.fiTotRef.setText(str(self.fiTotValue))
            self.input_fi.clear()

    def insertRunoutError(self):
        if (checkFloat(self.inputFr.text())):
            self.frValue = float(self.inputFr.text())
            self.frRef.setText(str(self.frValue))
            self.inputFr.clear()

    def timerSerialTick(self):
        try:
            if (self.ser.isOpen() and self.ser.inWaiting() > 0):
                while self.ser.isOpen() and self.ser.inWaiting() < 256:
                    pass
                bData = self.ser.read(self.ser.inWaiting())
                serData = bData.decode('utf-8').rstrip()
                tData = re.search('\r\n(.*)\r\n', serData).group(1)
                # if (checkFloat(tData)):
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
                if (checkFloat(tData)):
                    if (len(self.angles) <= 6):
                        self.angles = np.append(
                            self.angles, getlast(self.angles)+(np.pi/3))
                        self.values = np.append(self.values, float(tData))
                        self.ax1.plot(self.angles, self.values)
                        self.canvas.draw()
                    if (len(self.angles) == 6 and not self.isFill):
                        self.ax1.fill(self.angles, self.values, 'b', alpha=0.1)
                        self.isFill = True

                    self.isBegin = False
                    if (self.isRecord):
                        self.csv_log.loc[self.rowCount] = [
                            self.rowCount, tData, date.strftime('%H:%M:%S'), date.strftime('%d/%m/%Y')]
                        self.rowCount += 1

                    self.maximumData = float(tData) if float(
                        tData) > self.maximumData else self.maximumData
                    self.minimumData = float(tData) if float(
                        tData) < self.minimumData else self.minimumData
                    self.sumData += float(tData)
                    self.fiTotResult.setText('{:.2f}'.format(self.maximumData))
                    self.fiResult.setText('{:.2f}'.format(
                        self.maximumData-self.minimumData))
                    self.frResult.setText('{:.2f}'.format(
                        self.sumData/np.size(self.values)))
        except:
            pass

    def scanClick(self):
        portlist = self.getComPort()
        if (len(portlist) > 0):
            self.comboPort.addItems(portlist)
        else:
            self.errorPopup('Warning !!!', 'Com port not detected')

    def connectClick(self):
        # print('comport',self.comboPort.currentText())
        # print('baudrate',self.comboBaudRate.currentText())
        self.iconStatus.setPixmap(QtGui.QPixmap('resource/images/Green.png'))
        self.ser.open()
        self.connectBtn.setEnabled(False)
        while not self.ser.isOpen():
            pass
        self.labelStatus.setText('Status : Connected')
        self.angles = np.array([])
        self.values = np.array([])
        self.ax1.clear()
        self.canvas.draw()
        self.setToleranceValue()
        self.fiResult.setText('0.00')
        self.fiTotResult.setText('{:.2f}'.format(self.maximumData))
        self.frResult.setText('0.00')
        self.timerSerial.start(500)
        self.scanBtn.setEnabled(False)
        self.disconnectBtn.setEnabled(True)
        self.startBtn.setEnabled(True)
        self.isBegin = True

    def disconnectClick(self):
        self.iconStatus.setPixmap(QtGui.QPixmap('resource/images/Red.png'))
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
        self.recordIconStatus.setPixmap(
            QtGui.QPixmap('resource/images/Green.png'))
        self.startBtn.setEnabled(False)
        self.stopBtn.setEnabled(True)
        self.isRecord = True

    def stopClick(self):
        self.recordIconStatus.setPixmap(
            QtGui.QPixmap('resource/images/Red.png'))
        self.startBtn.setEnabled(True)
        self.stopBtn.setEnabled(False)
        self.isRecord = False

    def clearClick(self):
        self.isBegin = True
        self.tableData.setRowCount(0)
        self.tableData.insertRow(0)
        self.ax1.clear()
        self.canvas.draw()

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


def checkFloat(inputData):
    return re.search(r'^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$', inputData)


def getlast(data):
    return data[-1] if len(data) > 0 else (np.pi/30)*-1


if __name__ == '__main__':
    try:
        app = QtWidgets.QApplication(sys.argv)
        window = MyWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as err:
        print(err)
