import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from ErrorMessages import ValidateSpecialCase

excelDir = None


class Ui_SecondWindow(QtWidgets.QDialog):


    def setupUi(self, SecondWindow, excelDir):

        file = pd.ExcelFile(excelDir)
        self.sheets = file.sheet_names

        SecondWindow.setObjectName("SecondWindow")

        self.centralwidget = QtWidgets.QWidget(SecondWindow)
        self.centralwidget.setObjectName("centralwidget")
        SecondWindow.setCentralWidget(self.centralwidget)

        self.mainLaySW = QtWidgets.QVBoxLayout(self.centralwidget)

        # Font for Titles
        fontTitle = QtGui.QFont()
        fontTitle.setFamily("Arial")
        fontTitle.setPointSize(12)
        fontTitle.setBold(True)
        fontTitle.setWeight(75)

        # Font for text
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)

        self.header = QtWidgets.QLabel('Excel File Options')
        self.header.setFont(fontTitle)
        self.mainLaySW.addWidget(self.header)

        self.BaseCaseButton = QtWidgets.QRadioButton('Base Case (specification not needed)')
        self.BaseCaseButton.setFont(font)
        self.BaseCaseButton.clicked.connect(self.HideSpecialButtons)
        self.BaseCaseButton.setChecked(True)
        self.mainLaySW.addWidget(self.BaseCaseButton)

        self.SpecialCaseButton = QtWidgets.QRadioButton('Special Case (specify)')
        self.SpecialCaseButton.setFont(font)
        self.SpecialCaseButton.clicked.connect(self.ShowSpecialButtons)
        self.mainLaySW.addWidget(self.SpecialCaseButton)

        self.specialCaseOptions = QtWidgets.QGridLayout()
        self.sheetNameLabel = QtWidgets.QLabel('Sheet Name')
        self.sheetNameLabel.setFont(font)
        self.startRowLabel = QtWidgets.QLabel('Starting Row')
        self.startRowLabel.setFont(font)
        self.colNameLabel = QtWidgets.QLabel('Column Range')
        self.colNameLabel.setFont(font)

        self.SheetBox = QtWidgets.QComboBox()
        self.SheetBox.setFont(font)
        self.SheetBox.setObjectName("SheetBox")
        for sheet in self.sheets:
            self.SheetBox.addItem(sheet)
        self.SheetBox.show()

        self.RowText = QtWidgets.QLineEdit()
        self.RowText.setFont(font)
        self.ColumnText = QtWidgets.QLineEdit()
        self.ColumnText.setFont(font)

        self.notLabeledColumns = QtWidgets.QRadioButton('Not labeled Columns')
        self.labeledColumns = QtWidgets.QRadioButton('Labeled Columns')
        self.labeledColumns.setFont(font)
        self.notLabeledColumns.setFont(font)
        self.labeledColsGroup = QtWidgets.QButtonGroup()
        self.labeledColsGroup.addButton(self.notLabeledColumns)
        self.labeledColsGroup.addButton(self.labeledColumns)
        self.notLabeledColumns.setChecked(True)

        self.specialCaseOptions.addWidget(self.sheetNameLabel, 0, 0)
        self.specialCaseOptions.addWidget(self.SheetBox, 0, 1)
        self.specialCaseOptions.addWidget(self.startRowLabel, 1, 0)
        self.specialCaseOptions.addWidget(self.RowText, 1, 1)
        self.specialCaseOptions.addWidget(self.colNameLabel, 2, 0)
        self.specialCaseOptions.addWidget(self.ColumnText, 2, 1)
        self.specialCaseOptions.addWidget(self.notLabeledColumns, 3, 0)
        self.specialCaseOptions.addWidget(self.labeledColumns, 3, 1)
        self.mainLaySW.addLayout(self.specialCaseOptions)


        for i in range(self.specialCaseOptions.count()):
            widget = self.specialCaseOptions.itemAt(i).widget()
            if widget:
                widget.hide()


        self.pushButton = QtWidgets.QPushButton('OK', clicked = lambda: self.assign(SecondWindow))
        self.pushButton.setFont(fontTitle)
        self.mainLaySW.addWidget(self.pushButton)

        self.menubar = QtWidgets.QMenuBar(SecondWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 470, 26))
        self.menubar.setObjectName("menubar")
        SecondWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(SecondWindow)
        self.statusbar.setObjectName("statusbar")
        SecondWindow.setStatusBar(self.statusbar)
        QtCore.QMetaObject.connectSlotsByName(SecondWindow)

    def ShowSpecialButtons(self):
        for i in range(self.specialCaseOptions.count()):
            widget = self.specialCaseOptions.itemAt(i).widget()
            if widget:
                widget.show()

    def HideSpecialButtons(self):
        for i in range(self.specialCaseOptions.count()):
            widget = self.specialCaseOptions.itemAt(i).widget()
            if widget:
                widget.hide()

    def assign(self, swindow):
        if self.BaseCaseButton.isChecked():
            self.row = 0
            self.column = None
            self.sheet = self.sheets[0]
            swindow.close()

        if self.SpecialCaseButton.isChecked():
            columntext = self.ColumnText.text()
            rowtext = self.RowText.text()
            if ValidateSpecialCase(columntext, rowtext):
                self.row = self.RowText.text()
                self.column = columntext
                self.sheet = self.SheetBox.currentText()
                swindow.close()

        else:
            pass


if __name__ == "__main__":
    app2 = QtWidgets.QApplication(sys.argv)
    SecondWindow = QtWidgets.QMainWindow()
    ui = Ui_SecondWindow()
    ui.setupUi(SecondWindow, excelDir)
    SecondWindow.show()
    sys.exit(app2.exec_())
