import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import *

class Window(QWidget):
  def __init__(self, parent=None):
    super(Window, self).__init__(parent)

    leftLayout = QGridLayout()
    leftLayout.addWidget(self.connectionGroupe(), 0, 0)
    leftLayout.addWidget(self.calculationGroupe(), 1, 0)
    leftLayout.addLayout(self.recordingGroupe(), 2, 0)
    leftLayout.addWidget(self.dataTableGroupe(), 3, 0)

    rightLayout = QGridLayout()
    rightLayout.addWidget(self.graphGroupe(), 0, 0)

    grid = QGridLayout()
    grid.addLayout(leftLayout, 0, 0)
    grid.addLayout(rightLayout, 0, 1)
    self.setLayout(grid)

    self.left = 700
    self.top = 50
    self.width = 640
    self.height = 480
    self.initUI()

  def initUI(self):
    self.setWindowTitle('connection')
    # self.setGeometry(self.left, self.top, self.width, self.height)
    self.show()

  def connectionGroupe(self):
    connectionBox = QGroupBox('Connection')
    
    scanButton = QPushButton('Scan', self)
    scanButton.setToolTip('scanButton')
    scanButton.clicked.connect(self.scan_click)
    
    scanCB = QComboBox()
    # scanCB.currentIndexChanged.connect(self.selectionchange(scanCB))

    baudrateCB = QComboBox()

    baudrateLabel = QLabel("Baud Rate :", baudrateCB)

    connectionValueLayout = QHBoxLayout()
    connectionValueLayout.addWidget(scanButton)
    connectionValueLayout.addWidget(scanCB)
    connectionValueLayout.addWidget(baudrateLabel)
    connectionValueLayout.addWidget(baudrateCB)

    connectButton = QPushButton('Connect', self)
    connectButton.setToolTip('connect to arduino')
    connectButton.clicked.connect(self.scan_click)
    
    disconnectButton = QPushButton('Disconnect', self)
    disconnectButton.setToolTip('disconnect from arduino')
    disconnectButton.clicked.connect(self.scan_click)

    commandButtonLayout = QHBoxLayout()
    commandButtonLayout.addWidget(connectButton)
    commandButtonLayout.addWidget(disconnectButton)

    vbox = QVBoxLayout()
    vbox.addLayout(connectionValueLayout)
    vbox.addLayout(commandButtonLayout)
    vbox.addStretch(1)
    connectionBox.setLayout(vbox)
    return connectionBox

  def calculationGroupe(self):
    characterBox = QGroupBox('Characteristics')

    characterLayout = QVBoxLayout()

    characterRow1 = QHBoxLayout()
    picthText = QTextEdit()
    picthText.setFixedSize(80, 23)
    picthLabel = QLabel("Picth Diameter : Pd", picthText)
    picthResult = QLabel("Waitting...", picthText)
    characterRow1.addWidget(picthLabel)
    characterRow1.addWidget(picthText)
    characterRow1.addWidget(picthResult)
    characterLayout.addLayout(characterRow1)

    characterRow2 = QHBoxLayout()
    radialText = QTextEdit()
    radialText.setFixedSize(80, 23)
    radialLabel = QLabel("Radial Composite : Fi", radialText)
    radialResult = QLabel("Waitting...", picthText)
    characterRow2.addWidget(radialLabel)
    characterRow2.addWidget(radialText)
    characterRow2.addWidget(radialResult)
    characterLayout.addLayout(characterRow2)

    characterRow3 = QHBoxLayout()
    toothText = QTextEdit()
    toothText.setFixedSize(80, 23)
    toothLabel = QLabel("Tooth to tooth : fi", toothText)
    toothResult = QLabel("Waitting...", picthText)
    characterRow3.addWidget(toothLabel)
    characterRow3.addWidget(toothText)
    characterRow3.addWidget(toothResult)
    characterLayout.addLayout(characterRow3)

    characterRow4 = QHBoxLayout()
    runoutText = QTextEdit()
    runoutText.setFixedSize(80, 23)
    runoutLabel = QLabel("Ranout Error : Fr", runoutText)
    runoutResult = QLabel("Waitting...", picthText)
    characterRow4.addWidget(runoutLabel)
    characterRow4.addWidget(runoutText)
    characterRow4.addWidget(runoutResult)
    characterLayout.addLayout(characterRow4)

    characterBox.setLayout(characterLayout)
    return characterBox

  def recordingGroupe(self):
    grid = QGridLayout()

    recordingBox = QGroupBox('Recording')
    recordLayout = QVBoxLayout()
    recordRow1 = QHBoxLayout()
    startButton = QPushButton('Start', self)
    startButton.setToolTip('start record')
    startButton.clicked.connect(self.scan_click)

    stopButton = QPushButton('Stop', self)
    stopButton.setToolTip('stop record')
    stopButton.clicked.connect(self.scan_click)

    recordRow2 = QPushButton('Clear DataGridView and Graph', self)
    recordRow2.setToolTip('clear data')
    recordRow2.clicked.connect(self.scan_click)

    recordRow1.addWidget(startButton)
    recordRow1.addWidget(stopButton)
    recordLayout.addLayout(recordRow1)
    recordLayout.addWidget(recordRow2)
    recordingBox.setLayout(recordLayout)

    exportBox = QGroupBox('Export')
    exportBox.setFixedWidth(120)
    exportLayout = QVBoxLayout()
    exportButton = QPushButton('Save To MS\nExcel', self)
    exportButton.setToolTip('export record')
    exportButton.clicked.connect(self.scan_click)
    exportLayout.addWidget(exportButton)
    exportBox.setLayout(exportLayout)

    grid.addWidget(recordingBox, 0, 0)
    grid.addWidget(exportBox, 0, 1)
    return grid

  def dataTableGroupe(self):
    tableBox = QGroupBox('Data Grid View (Real-Time/Second)')
    layout = QVBoxLayout()

    tableHeader = ['No', 'VALUE    ', 'TIME      ', 'DATE']

    table = QTableWidget(self)
    table.setColumnCount(len(tableHeader))
    table.setRowCount(3)
    table.setHorizontalHeaderLabels(tableHeader)
    table.resizeColumnsToContents()

    layout.addWidget(table)
    tableBox.setLayout(layout)
    return tableBox

  def graphGroupe(self):
    groupBox = QGroupBox('Graph (Real-Time/Second)')
    groupBox.setFixedWidth(400)
    textEdit = QTextEdit()
    textEdit.setFixedHeight(480)
    
    vbox = QVBoxLayout()
    vbox.addWidget(textEdit)
    vbox.setContentsMargins(5, 5, 5, 5)
    vbox.addStretch(1)
    groupBox.setLayout(vbox)
    return groupBox

  @pyqtSlot()
  def scan_click(self):
    print(type(self.width.real))

  def selectionchange(self,cb, i):
    print("Items in the list are :")

    for count in range(self.cb.count()):
      print(cb.itemText(count))
    print("Current index",i,"selection changed ",cb.currentText())
 
if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = Window()
  sys.exit(app.exec_())