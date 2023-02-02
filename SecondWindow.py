import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from ErrorMessages import ValidateSpecialCase


excelDir = "Test1.xlsx"

class Ui_SecondWindow(object):


    def setupUi(self, SecondWindow, excelDir):

        file = pd.ExcelFile(excelDir)
        self.sheets = file.sheet_names
        SecondWindow.setObjectName("SecondWindow")
        SecondWindow.resize(470, 200)
        self.centralwidget = QtWidgets.QWidget(SecondWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(20, 0, 381, 291))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(100, 10, 161, 41))
        font = QtGui.QFont()
        font.setFamily("Yu Gothic UI Semibold")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label.setWordWrap(False)
        self.label.setObjectName("label")
        self.BaseCaseButton = QtWidgets.QRadioButton(self.frame, clicked = lambda: self.HideSpecialButtons())
        self.BaseCaseButton.setGeometry(QtCore.QRect(20, 60, 261, 20))
        self.BaseCaseButton.setObjectName("BaseCaseButton")
        self.BaseCaseButton.setChecked(True)
        self.SpecialCaseButton = QtWidgets.QRadioButton(self.frame, clicked = lambda: self.ShowSpecialButtons(SecondWindow))
        self.SpecialCaseButton.setGeometry(QtCore.QRect(20, 90, 261, 20))
        self.SpecialCaseButton.setObjectName("SpecialCaseButton")
        self.pushButton = QtWidgets.QPushButton(self.frame, clicked = lambda: self.assign(SecondWindow))
        self.pushButton.setGeometry(QtCore.QRect(200, 130, 93, 28))
        self.pushButton.setObjectName("pushButton")
        SecondWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(SecondWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 470, 26))
        self.menubar.setObjectName("menubar")
        SecondWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(SecondWindow)
        self.statusbar.setObjectName("statusbar")
        SecondWindow.setStatusBar(self.statusbar)

        self.retranslateUi(SecondWindow)
        QtCore.QMetaObject.connectSlotsByName(SecondWindow)

        self.specialButtonsBool = False


    def ShowSpecialButtons(self, SecondWindow):
        self.specialButtonsBool = True
        SecondWindow.resize(470, 310)
        self.pushButton.setGeometry(QtCore.QRect(200, 250, 93, 28))
        self.SheetBox = QtWidgets.QComboBox(self.frame)
        self.SheetBox.setGeometry(QtCore.QRect(150, 130, 191, 21))
        self.SheetBox.setObjectName("SheetBox")
        for sheet in self.sheets:
            self.SheetBox.addItem(sheet)
        self.SheetBox.show()
        self.RowText = QtWidgets.QLineEdit(self.frame)
        self.RowText.setGeometry(QtCore.QRect(150, 170, 191, 22))
        self.RowText.setObjectName("RowText")
        self.RowText.show()
        self.ColumnText = QtWidgets.QLineEdit(self.frame)
        self.ColumnText.setGeometry(QtCore.QRect(150, 210, 191, 22))
        self.ColumnText.setObjectName("ColumnText")
        self.ColumnText.show()

        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(30, 130, 111, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(30, 170, 111, 16))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.frame)
        self.label_4.setGeometry(QtCore.QRect(30, 210, 111, 16))
        self.label_4.setObjectName("label_4")

        self.label_2.setText("Sheet Name")
        self.label_3.setText("Starting Row")
        self.label_4.setText("Column Range")

        self.label_2.show()
        self.label_3.show()
        self.label_4.show()

    def HideSpecialButtons(self):
        SecondWindow.resize(470, 200)
        self.pushButton.setGeometry(QtCore.QRect(200, 130, 93, 28))

        if self.specialButtonsBool:
            self.SheetBox.hide()
            self.RowText.hide()
            self.ColumnText.hide()
            self.label_2.hide()
            self.label_3.hide()
            self.label_4.hide()


    def assign(self, swindow):
        if self.BaseCaseButton.isChecked():
            self.row = 0
            self.column = None
            self.sheet = self.sheets[0]

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

    def retranslateUi(self, SecondWindow):
        _translate = QtCore.QCoreApplication.translate
        SecondWindow.setWindowTitle(_translate("SecondWindow", "MainWindow"))
        self.label.setText(_translate("SecondWindow", "Excel File Options"))
        self.BaseCaseButton.setText(_translate("SecondWindow", "Base Case (specification not needed)"))
        self.SpecialCaseButton.setText(_translate("SecondWindow", "Special Case (specify)"))
        self.pushButton.setText(_translate("SecondWindow", "OK"))


if __name__ == "__main__":
    app2 = QtWidgets.QApplication(sys.argv)
    SecondWindow = QtWidgets.QMainWindow()
    ui = Ui_SecondWindow()
    ui.setupUi(SecondWindow, excelDir)
    SecondWindow.show()
    sys.exit(app2.exec_())
