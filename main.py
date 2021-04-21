import re
import pandas as pd
import sys
import numpy as np
import serial
import glob
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from datetime import datetime as Date

import time
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
matplotlib.use('QT5Agg')

isRecord = False
connectionStatus = False


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.set_ylim(bottom=-10, top=10)
        super(MplCanvas, self).__init__(fig)


class ConnectSerial(QtCore.QObject):
    end = QtCore.pyqtSignal()

    def __init__(self, serial):
        super().__init__()
        self.ser = serial

    def run(self):
        self.ser.open()
        start_time = Date.now()

        confirmString = ''
        global connectionStatus
        connectionStatus = True
        while not '.c.' in confirmString:
            if (self.ser.inWaiting() > 0):
                confirmString += self.ser.read(1).decode('utf-8')
            time_delta = Date.now() - start_time
            if time_delta.total_seconds() >= 5:
                connectionStatus = False
                break
        self.end.emit()


class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(str, Date)
    updatePlot = QtCore.pyqtSignal(str)

    def __init__(self, serial):
        super().__init__()
        self.ser = serial

    def run(self):
        global isRecord
        data = ""
        self.ser.flushInput()
        self.ser.flushOutput()
        while (isRecord):
            if (self.ser.isOpen() and self.ser.inWaiting() > 0):
                data = self.ser.readline().decode('utf-8')
                if ('.s.' in data):
                    isRecord = False
                    break
                stripData = data.rstrip("\r\n")
                self.progress.emit(stripData, Date.now())
                self.updatePlot.emit(stripData)
        self.finished.emit()


class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi("resource/mainQt.ui", self)
        # test data
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.lay = QtWidgets.QVBoxLayout(self.content_plot)
        self.lay.addWidget(self.canvas)
        self.initialGraph()

        # set default variable
        self.rowCount = 1
        self.csv_log = pd.DataFrame(columns=['No', 'Value', 'Time', 'Date'])
        self.setToleranceValue()
        self.previousTime = Date.now()

        self.ser = serial.Serial()

        # setup callback function
        self.scanBtn.clicked.connect(self.scanClick)
        self.connectBtn.clicked.connect(self.connectClick)
        self.disconnectBtn.clicked.connect(self.disconnectClick)
        self.comboPort.currentTextChanged.connect(self.comboPortChange)
        self.comboBaudRate.currentTextChanged.connect(self.comboBaudRateChange)
        self.startBtn.clicked.connect(self.startClick)
        self.stopBtn.clicked.connect(self.stopClick)
        self.clearBtn.clicked.connect(self.clearClick)
        self.exportBtn.clicked.connect(self.exportClick)
        self.inputPd.returnPressed.connect(self.insertPicthDiameter)
        self.inputGearTeeth.returnPressed.connect(self.insertGearTeeth)
        self.inputFi.returnPressed.connect(self.insertRadialComposite)
        self.input_fi.returnPressed.connect(self.insertToothToTooth)
        self.inputFr.returnPressed.connect(self.insertRunoutError)

    def initialGraph(self):
        n_data = 60
        self.x_angles = list(range(n_data))
        self.y_values = [0.0 for i in range(n_data)]
        self._plot_ref = None
        self.update_plot(0.0)

    def update_plot(self, getData):
        self.y_values = self.y_values[1:] + [float(getData)]
        if (self._plot_ref is None):
            plot_refs = self.canvas.axes.plot(
                self.x_angles, self.y_values, 'r')
            self._plot_ref = plot_refs[0]
        else:
            self._plot_ref.set_ydata(self.y_values)
        self.canvas.draw()

    def addDataTable(self, data, datetime):
        rowPosition = self.tableData.rowCount()
        self.tableData.insertRow(rowPosition)

        self.tableData.setItem(
            rowPosition, 0, QtWidgets.QTableWidgetItem(data))
        self.tableData.setItem(
            rowPosition, 1, QtWidgets.QTableWidgetItem(datetime.strftime('%H:%M:%S')))
        self.tableData.setItem(
            rowPosition, 2, QtWidgets.QTableWidgetItem(datetime.strftime('%d/%m/%Y')))
        self.tableData.scrollToBottom()

        self.maximumData = float(data) if float(
            data) > self.maximumData else self.maximumData
        self.minimumData = float(data) if float(
            data) < self.minimumData else self.minimumData
        self.sumData += float(data)
        self.fiTotResult.setText('{:.2f}'.format(self.maximumData))
        self.fiResult.setText('{:.2f}'.format(
            self.maximumData-self.minimumData))
        self.frResult.setText('{:.2f}'.format(
            self.sumData/np.size(self.y_values)))

    def scanClick(self):
        portlist = self.getComPort()
        if (len(portlist) > 0):
            self.comboPort.addItems(portlist)
        else:
            self.errorPopup('Warning !!!', 'Com port not detected')

    def serialConnected(self):
        if (connectionStatus):
            self.iconStatus.setPixmap(
                QtGui.QPixmap('resource/images/Green.png'))
            self.labelStatus.setText('Status : Connected')
            self.setToleranceValue()
            self.fiResult.setText('0.00')
            self.fiTotResult.setText('{:.2f}'.format(self.maximumData))
            self.frResult.setText('0.00')
            self.scanBtn.setEnabled(False)
            self.disconnectBtn.setEnabled(True)
            self.startBtn.setEnabled(True)
        else:
            self.ser.close()
            self.connectBtn.setEnabled(True)
            self.errorPopup('Connection fail!!!', 'Request time-out')
        QtWidgets.QApplication.restoreOverrideCursor()

    def connectClick(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.connectBtn.setEnabled(False)
        # initial thread
        self.threadConnect = QtCore.QThread()
        self.connectSerial = ConnectSerial(self.ser)
        self.connectSerial.moveToThread(self.threadConnect)

        self.threadConnect.started.connect(self.connectSerial.run)
        self.connectSerial.end.connect(self.threadConnect.quit)
        self.connectSerial.end.connect(self.connectSerial.deleteLater)
        self.threadConnect.finished.connect(self.threadConnect.deleteLater)

        # start thread
        self.threadConnect.start()

        self.threadConnect.finished.connect(self.serialConnected)

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
        if (isRecord):
            self.stopClick()

    def comboPortChange(self):
        self.ser.port = self.comboPort.currentText()
        self.comboBaudRate.clear()
        self.comboBaudRate.addItems(['300', '1200', '2400', '4800', '9600', '19200', '38400', '57600',
                                     '74880', '115200', '230400', '250000', '500000', '1000000', '2000000'])
        self.comboBaudRate.setCurrentIndex(9)
        self.connectBtn.setEnabled(True)

    def comboBaudRateChange(self):
        self.ser.baudrate = int(self.comboBaudRate.currentText())

    def startClick(self):
        # self.tableData.setRowCount(0)
        self.clearClick()
        # initial thread
        self.thread = QtCore.QThread()
        self.worker = Worker(self.ser)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.addDataTable)
        self.worker.updatePlot.connect(self.update_plot)

        # start thread
        self.ser.write(b'start\n')
        time.sleep(.1)
        global isRecord
        isRecord = True
        self.thread.start()

        # Final resets
        self.recordIconStatus.setPixmap(
            QtGui.QPixmap('resource/images/Green.png'))
        self.startBtn.setEnabled(False)
        self.stopBtn.setEnabled(True)
        self.thread.finished.connect(self.stopClick)

    def stopClick(self):
        self.ser.write(b'stop\n')
        self.recordIconStatus.setPixmap(
            QtGui.QPixmap('resource/images/Red.png'))
        self.startBtn.setEnabled(True)
        self.stopBtn.setEnabled(False)

    def clearClick(self):
        self.tableData.setRowCount(0)
        n_data = 60
        self.x_angles = list(range(n_data))
        self.y_values = [0.0 for i in range(n_data)]
        self.update_plot(0.0)

    def exportClick(self):
        rowCount = self.tableData.rowCount()
        columnCount = self.tableData.columnCount()
        for row in range(rowCount):
            rowData = [row+1]
            for column in range(columnCount):
                rowData.append(self.tableData.item(row, column).text(
                ) if column != 0 else float(self.tableData.item(row, column).text()))
            self.csv_log.loc[row] = rowData
        pathName = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Choose location to save csv file', filter="CSV Files (*.csv)")
        if (pathName[1] != ''):
            resultPath = pathName[0][:pathName[0].rfind('.')] + '.csv'
            self.csv_log.to_csv(
                resultPath, index=False, header=True)

    def insertPicthDiameter(self):
        if (checkFloat(self.inputPd.text())):
            self.pdValue = float(self.inputPd.text())
            self.pdResult.setText(str(self.pdValue))
            self.inputPd.clear()

    def setToleranceValue(self, maximun=0.00, minimun=9999.00, summary=0.00):
        self.maximumData = maximun
        self.minimumData = minimun
        self.sumData = summary

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

    def errorPopup(self, title, text):
        error_dialog = QtWidgets.QMessageBox()
        error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
        error_dialog.setWindowTitle(title)
        error_dialog.setText(text)
        error_dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)

        error_dialog.exec_()

    def getComPort(self):
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
