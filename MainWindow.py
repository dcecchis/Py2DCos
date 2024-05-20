from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QGridLayout, QWidget, QPushButton, \
    QLabel, QRadioButton, QSizePolicy, QSlider, QComboBox, QFileDialog, QButtonGroup, QSpacerItem
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtCore import QSize
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from ErrorMessages import ValidateExtension
from twoDspeciesNEW import twoDspecies
from SecondWindow import Ui_SecondWindow
import matplotlib.pyplot as plt

## List of line_color supported
color_list = ["navy", 'black', "white", "red", "lime", "blue", "yellow", "maroon", "olive",
              "green", "teal"]
## List of cmap supported
cmap_list = ['bwr', 'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu',
             'RdYlGn', 'Spectral', 'coolwarm', 'seismic']

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 y Matplotlib")

        self.central_widget = QWidget()
        self.central_widget.setMinimumSize(QSize(600, 400))
        self.setCentralWidget(self.central_widget)

        self.mainLay = QHBoxLayout(self.central_widget)  # Main Layout, horizontal

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

        # Only creating the left layout
        self.leftLay = QVBoxLayout()
        self.mainLay.addLayout(self.leftLay, 1)
        self.leftLay.setAlignment(Qt.AlignTop)
        # self.leftLay.setAlignment(Qt.AlignCenter)

        # Creation of right layout, which contains canvas and toolbar
        self.rightLay = QVBoxLayout()
        # Creation of Canvas
        self.figure = plt.figure()
        self.figure.set_facecolor("#f0f0f0")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.rightLay.addWidget(self.canvas)

        #Creation of Toolbar
        self.toolbarLayout = QHBoxLayout()
        self.rightLay.addLayout(self.toolbarLayout)
        self.toolbar = NavigationToolbar(self.canvas, None)
        self.triDbutton = QPushButton('3D Plot')
        self.toolbarLayout.addWidget(self.toolbar, alignment=Qt.AlignRight)
        self.toolbarLayout.addWidget(self.triDbutton, alignment=Qt.AlignLeft)


        self.mainLay.addLayout(self.rightLay, 5)

        # NOW WORKING ON LEFT LAYOUT
        spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding)

        ##### CORRELATION TYPE #####
        # self.leftLay.addItem(spacer)
        self.corrTypeLayout = QVBoxLayout()  # Will contain label and radio buttons for Corr Type
        corrTypeLabel = QLabel('Correlation Type')
        corrTypeLabel.setFont(fontTitle)
        self.corrTypeLayout.addWidget(corrTypeLabel, alignment=Qt.AlignCenter)

        self.corrTypeButtonsLayout = QHBoxLayout()
        self.homoCorrButton = QRadioButton('Homocorrelation')
        self.homoCorrButton.setFont(font)
        self.heteroCorrButton = QRadioButton('Heterocorrelation')
        self.heteroCorrButton.setFont(font)
        self.corrTypeButtonsLayout.addWidget(self.homoCorrButton)
        self.corrTypeButtonsLayout.addWidget(self.heteroCorrButton)
        self.corrTypeLayout.addLayout(self.corrTypeButtonsLayout)

        self.leftLay.addLayout(self.corrTypeLayout)  # Adding to self.leftLayout

        self.leftLay.addItem(spacer)

        ##### CALCULATION METHOD #####
        self.calcMethodLayout = QVBoxLayout()  # Will contain label and radio buttons for Calc Method
        self.calcMethodLabel = QLabel('Calculation Method')
        self.calcMethodLabel.setFont(fontTitle)
        self.calcMethodLayout.addWidget(self.calcMethodLabel, alignment=Qt.AlignCenter)

        self.calcMethodButtonsLayout = QHBoxLayout()
        self.hilbertTransformButton = QRadioButton('Hilbert Transform')
        self.hilbertTransformButton.setFont(font)
        self.fftButton = QRadioButton('FFT')
        self.fftButton.setFont(font)
        self.calcMethodButtonsLayout.addWidget(self.hilbertTransformButton)
        self.calcMethodButtonsLayout.addWidget(self.fftButton)
        self.calcMethodLayout.addLayout(self.calcMethodButtonsLayout)

        self.leftLay.addLayout(self.calcMethodLayout)
        self.leftLay.addItem(spacer)

        #### INPUT FILES #####
        self.inputFilesLayout = QVBoxLayout()  # Will contain label and buttons for input files
        self.inputFilesLabel = QLabel('Input')
        self.inputFilesLabel.setFont(fontTitle)
        self.inputFilesLayout.addWidget(self.inputFilesLabel, alignment=Qt.AlignCenter)

        self.file1Button = QPushButton('Choose your File')
        self.file1Button.setMinimumSize(250, 30)
        self.file1Button.setFont(font)
        self.inputFilesLayout.addWidget(self.file1Button)

        self.file2Button = QPushButton('Choose your file')
        self.file2Button.setFont(font)
        self.file2Button.setMinimumSize(250, 30)
        self.inputFilesLayout.addWidget(self.file2Button)
        self.file2Button.hide()


        self.leftLay.addLayout(self.inputFilesLayout)
        self.leftLay.addItem(spacer)

        ##### REFERENCE SPECTRA #####
        self.referenceSpectraLayout = QVBoxLayout()  # Will contain label and buttons for reference spectra
        self.referenceSpectraLabel = QLabel('Reference Spectra')
        self.referenceSpectraLabel.setFont(fontTitle)
        self.referenceSpectraLayout.addWidget(self.referenceSpectraLabel, alignment=Qt.AlignCenter)

        self.referenceSpectraButtonsLayout = QGridLayout()
        self.meanButton = QRadioButton('Mean')
        self.meanButton.setFont(font)
        self.zeroButton = QRadioButton('Zero')
        self.zeroButton.setFont(font)
        self.initialButton = QRadioButton('Initial')
        self.initialButton.setFont(font)
        self.finalButton = QRadioButton('Final')
        self.finalButton.setFont(font)
        self.referenceSpectraButtonsLayout.addWidget(self.meanButton, 0, 0)
        self.referenceSpectraButtonsLayout.addWidget(self.zeroButton, 0, 1)
        self.referenceSpectraButtonsLayout.addWidget(self.initialButton, 1, 0)
        self.referenceSpectraButtonsLayout.addWidget(self.finalButton, 1, 1)
        self.referenceSpectraLayout.addLayout(self.referenceSpectraButtonsLayout)

        self.leftLay.addLayout(self.referenceSpectraLayout)
        self.leftLay.addItem(spacer)

        # OK BUTTON
        self.plotButton = QPushButton('OK')  # Button for plotting
        self.plotButton.setFont(fontTitle)
        self.plotButton.setMaximumSize(250, 50)
        self.plotButton.setMinimumSize(250, 50)
        self.leftLay.addWidget(self.plotButton, alignment=Qt.AlignHCenter)
        self.leftLay.addItem(spacer)

        ###### GRAPH SETTINGS ######
        self.graphSettingsLayout = QVBoxLayout()  # will contain label and: number of contours, color map, contour lines color, color intensity, contour lines intensity
        self.graphSettingsLabel = QLabel('Graph Settings')
        self.graphSettingsLabel.setFont(fontTitle)
        self.graphSettingsLayout.addWidget(self.graphSettingsLabel, alignment=Qt.AlignCenter)

        self.graphSettingsGrid = QGridLayout()
        #Number of contours (slider)
        self.numOfContoursSlider = QSlider()
        self.numOfContoursSlider.setOrientation(1)
        self.numOfContoursSlider.setMinimum(1)
        self.numOfContoursSlider.setMaximum(40)
        self.numOfContoursSlider.setValue(6)
        self.graphSettingsGrid.addWidget(self.numOfContoursSlider, 0, 1)
        self.numOfContoursLabel = QLabel('Number of Contours: '+str(self.numOfContoursSlider.value()))
        self.numOfContoursLabel.setFont(font)
        self.graphSettingsGrid.addWidget(self.numOfContoursLabel, 0, 0)

        #Color Map (combo box)
        self.colorMapLabel = QLabel('Color Map')
        self.colorMapLabel.setFont(font)
        self.graphSettingsGrid.addWidget(self.colorMapLabel, 1, 0)
        self.colorMapBox = QComboBox()
        self.colorMapBox.setFont(font)
        for cmap in cmap_list:
            self.colorMapBox.addItem(cmap)
        self.graphSettingsGrid.addWidget(self.colorMapBox, 1, 1)

        # Contour Lines Color (combo box)
        self.contourLinesColorLabel = QLabel('Contour Lines Color')
        self.contourLinesColorLabel.setFont(font)
        self.graphSettingsGrid.addWidget(self.contourLinesColorLabel, 2, 0)
        self.contourLinesColorBox = QComboBox()
        self.contourLinesColorBox.setFont(font)
        for cline in color_list:
            self.contourLinesColorBox.addItem(cline)
        self.graphSettingsGrid.addWidget(self.contourLinesColorBox, 2, 1)

        #Color Intensity (slider)
        self.colorIntensitySlider = QSlider()
        self.colorIntensitySlider.setOrientation(1)
        self.colorIntensitySlider.setMinimum(1)
        self.colorIntensitySlider.setMaximum(100)
        self.colorIntensitySlider.setValue(100)
        self.graphSettingsGrid.addWidget(self.colorIntensitySlider, 3, 1)
        self.colorIntensityLabel = QLabel('Color Intensity: '+str(self.colorIntensitySlider.value()))
        self.colorIntensityLabel.setFont(font)
        self.graphSettingsGrid.addWidget(self.colorIntensityLabel, 3, 0)

        #Contour Lines Intensity (slider)
        self.contourLinesIntensitySlider = QSlider()
        self.contourLinesIntensitySlider.setOrientation(1)
        self.contourLinesIntensitySlider.setMinimum(1)
        self.contourLinesIntensitySlider.setMaximum(100)
        self.contourLinesIntensitySlider.setValue(60)
        self.graphSettingsGrid.addWidget(self.contourLinesIntensitySlider, 4, 1)
        self.contourLinesIntensityLabel = QLabel('Contour Lines Intensity: '+str(self.contourLinesIntensitySlider.value()))
        self.contourLinesIntensityLabel.setFont(font)
        self.graphSettingsGrid.addWidget(self.contourLinesIntensityLabel, 4, 0)

        self.graphSettingsLayout.addLayout(self.graphSettingsGrid)
        self.leftLay.addLayout(self.graphSettingsLayout)
        self.leftLay.addItem(spacer)

        ### DIAGONALS AND AXES ###
        self.diagsandAxisLayout = QVBoxLayout()
        self.diagsAndAxesLabel = QLabel('Diagonals and axes')
        self.diagsAndAxesLabel.setFont(font)
        self.diagsAndAxesLabel.setFont(fontTitle)
        self.diagsandAxisLayout.addWidget(self.diagsAndAxesLabel, alignment=Qt.AlignCenter)

        self.diagsandAxesOptionsGrid = QGridLayout()
        self.syncDiagLabel = QLabel("Sync: ")
        self.syncDiagLabel.setFont(font)
        self.asyncDiagLabel = QLabel("Async: ")
        self.asyncDiagLabel.setFont(font)
        self.xAxisLabel = QLabel('X axis:')
        self.xAxisLabel.setFont(font)
        self.syncMainDiagButton = QRadioButton('Main Diag')
        self.syncMainDiagButton.setFont(font)
        self.syncAntidiagButton = QRadioButton('Antidiag')
        self.syncAntidiagButton.setFont(font)
        self.asyncMainDiagButton = QRadioButton('Main Diag')
        self.asyncMainDiagButton.setFont(font)
        self.asyncAntidiagButton = QRadioButton('Antidiag')
        self.asyncAntidiagButton.setFont(font)
        self.increasingXbutton = QRadioButton('Increasing')
        self.increasingXbutton.setFont(font)
        self.decreasingXbutton = QRadioButton('Decreasing')
        self.decreasingXbutton.setFont(font)
        self.diagsandAxesOptionsGrid.addWidget(self.syncDiagLabel, 0, 0)
        self.diagsandAxesOptionsGrid.addWidget(self.syncMainDiagButton, 0, 1)
        self.diagsandAxesOptionsGrid.addWidget(self.syncAntidiagButton, 0, 2)
        self.diagsandAxesOptionsGrid.addWidget(self.asyncDiagLabel, 1, 0)
        self.diagsandAxesOptionsGrid.addWidget(self.asyncMainDiagButton, 1, 1)
        self.diagsandAxesOptionsGrid.addWidget(self.asyncAntidiagButton, 1, 2)
        self.diagsandAxesOptionsGrid.addWidget(self.xAxisLabel, 2, 0)
        self.diagsandAxesOptionsGrid.addWidget(self.increasingXbutton, 2, 1)
        self.diagsandAxesOptionsGrid.addWidget(self.decreasingXbutton, 2, 2)

        self.diagsandAxisLayout.addLayout(self.diagsandAxesOptionsGrid)

        self.leftLay.addLayout(self.diagsandAxisLayout)
        self.leftLay.addItem(spacer)

        ### SHOWN GRAPH ###
        self.shownGraphLayout = QVBoxLayout()
        self.shownGraphLabel = QLabel('Shown Graph')
        self.shownGraphLabel.setFont(fontTitle)
        self.shownGraphLayout.addWidget(self.shownGraphLabel, alignment=Qt.AlignCenter)

        self.shownGraphOptionsLayout = QHBoxLayout()
        self.syncGraphOption = QRadioButton('Sync')
        self.syncGraphOption.setFont(font)
        self.asyncGraphOption = QRadioButton('Async')
        self.asyncGraphOption.setFont(font)
        self.bothGraphOption = QRadioButton('Both')
        self.bothGraphOption.setFont(font)
        self.shownGraphOptionsLayout.addWidget(self.syncGraphOption)
        self.shownGraphOptionsLayout.addWidget(self.asyncGraphOption)
        self.shownGraphOptionsLayout.addWidget(self.bothGraphOption)
        self.shownGraphLayout.addLayout(self.shownGraphOptionsLayout)

        self.leftLay.addLayout(self.shownGraphLayout)
        self.leftLay.addItem(spacer)

    ### BUTTON GROUPS ###
        # Correlation type buttons
        self.corrTypeGroup = QButtonGroup()
        self.corrTypeGroup.addButton(self.homoCorrButton)
        self.corrTypeGroup.addButton(self.heteroCorrButton)
        self.corrTypeGroup.setExclusive(True)

        # Calculation method group
        self.calcMethodGroup = QButtonGroup()
        self.calcMethodGroup.addButton(self.hilbertTransformButton)
        self.calcMethodGroup.addButton(self.fftButton)
        self.calcMethodGroup.setExclusive(True)

        # File input group
        self.fileGroup = QButtonGroup()
        self.fileGroup.addButton(self.file1Button)
        self.fileGroup.addButton(self.file2Button)

        # Reference spectra group
        self.referenceSpectraGroup = QButtonGroup()
        self.referenceSpectraGroup.addButton(self.meanButton)
        self.referenceSpectraGroup.addButton(self.zeroButton)
        self.referenceSpectraGroup.addButton(self.initialButton)
        self.referenceSpectraGroup.addButton(self.finalButton)
        self.referenceSpectraGroup.setExclusive(True)

        # Synchronous diagonals group
        self.syncDiagonalsGroup = QButtonGroup()
        self.syncDiagonalsGroup.addButton(self.syncMainDiagButton)
        self.syncDiagonalsGroup.addButton(self.syncAntidiagButton)
        self.syncDiagonalsGroup.setExclusive(True)

        # Asynchronous diagonals group
        self.asyncDiagonalsGroup = QButtonGroup()
        self.asyncDiagonalsGroup.addButton(self.asyncMainDiagButton)
        self.asyncDiagonalsGroup.addButton(self.asyncAntidiagButton)
        self.asyncDiagonalsGroup.setExclusive(True)

        # X axis tendency group
        self.xAxisGroup = QButtonGroup()
        self.xAxisGroup.addButton(self.increasingXbutton)
        self.xAxisGroup.addButton(self.decreasingXbutton)
        self.xAxisGroup.setExclusive(True)

        # Shown graph group
        self.shownGraphGroup = QButtonGroup()
        self.shownGraphGroup.addButton(self.syncGraphOption)
        self.shownGraphGroup.addButton(self.asyncGraphOption)
        self.shownGraphGroup.addButton(self.bothGraphOption)
        self.shownGraphGroup.setExclusive(True)



        ### DEFAULT BUTTONS ###
        # Correlation Type default: homo
        self.homoCorrButton.setChecked(True)
        # Calculation Method default: HT
        self.hilbertTransformButton.setChecked(True)
        # Reference Spectra default: initial
        self.initialButton.setChecked(True)
        # Color Map default: coolwarm
        self.colorMapBox.setCurrentText('coolwarm')
        # Contour Lines color default: black
        self.contourLinesColorBox.setCurrentText('black')
        # Synchronous diagonal default: main diag
        self.syncMainDiagButton.setChecked(True)
        # Asynchronous diagonal default: antidiag
        self.asyncAntidiagButton.setChecked(True)
        # X axis tendency default: increasing
        self.decreasingXbutton.setChecked(True)
        # Shown Graph default: both
        self.bothGraphOption.setChecked(True)


    ### ADDING FUNCTIONALITY TO BUTTONS ###
        # Show or hide second file
        self.homoCorrButton.clicked.connect(self.changeHeteroUpload)
        self.heteroCorrButton.clicked.connect(self.changeHeteroUpload)

        # Upload files
        self.file1Button.clicked.connect(self.uploadFile)
        self.file2Button.clicked.connect(self.uploadFile)

        # Sliders
        self.numOfContoursSlider.valueChanged.connect(self.changeSliders)
        self.colorIntensitySlider.valueChanged.connect(self.changeSliders)
        self.contourLinesIntensitySlider.valueChanged.connect(self.changeSliders)

        # changing status
        self.corrTypeGroup.buttonClicked.connect(self.changeStatus)
        self.referenceSpectraGroup.buttonClicked.connect(self.changeStatus)
        self.calcMethodGroup.buttonClicked.connect(self.changeStatus)
        self.syncDiagonalsGroup.buttonClicked.connect(self.changeStatus)
        self.asyncDiagonalsGroup.buttonClicked.connect(self.changeStatus)
        self.xAxisGroup.buttonClicked.connect(self.changeStatus)
        self.shownGraphGroup.buttonClicked.connect(self.changeStatus)
        self.colorMapBox.activated[str].connect(self.changeStatus)
        self.contourLinesColorBox.activated[str].connect(self.changeStatus)

        #plot button
        self.plotButton.clicked.connect(self.plotButtonFunction)

        #3D plot
        self.triDbutton.clicked.connect(self.show3D)

    ### SOME AUXILIAR VARIABLES
        # auxiliar variables needed
        self.auxvar = False  # used for avoiding bug if changing setting options before plotting
        self.filename1 = ""
        self.filename2 = ""
        self.type1 = ""
        self.type2 = ""

    ### Actual State Of the Plotting Variables
        self.status = {
            'corrType': 'homo',
            'calcMethod': 'HT',
            'refSpectra': 'ini',
            'colorMap': 'coolwarm',
            'numOfContour': 6,
            'syncDiag': 'main',
            'asyncDiag': 'anti',
            'xAxis': 'decreasing',
            'colorMapIntensity': 1.0,
            'colorLines': 'black',
            'colorLinesIntensity': 0.6,
            'shownGraph': 'both',
            'canvas': True,
            'figure': self.figure
        }


    def uploadFile(self):
        # open file dialog
        filename = QFileDialog.getOpenFileName(window, "Open File", "",
                                               "All Files (*);; Excel files (*.xlsx);; CSV files (*.csv);; txt files (*.txt)")
        if filename:
            word = str(filename[0])
            lastSlash = word[::-1].find("/")
            name = word[len(word) - lastSlash:]
            if name != "":
                if self.sender() == self.file1Button:
                    self.type1 = self.getType(word)
                    self.file1Button.setText(name)
                    self.filename1 = [filename[0], self.type1]

                    if self.type1 == "xlsx":
                        self.OpenSecondWindow(self.filename1[0])
                else:
                    self.type2 = self.getType(word)
                    self.file2Button.setText(name)
                    self.filename2 = [filename[0], self.type2]

                    if self.type2 == "xlsx":
                        self.OpenSecondWindow(self.filename2[0])
            else:
                pass

    def getType(self, word):
        c = word[::-1].find(".")
        return word[len(word) - c:]


    def changeHeteroUpload(self): # shows or hide second button for uploading file
        if self.sender() == self.homoCorrButton:
            self.file2Button.hide()
        else:
            self.file2Button.show()


    def OpenSecondWindow(self, excelDir): # this function executes when an excel file was uploaded
        self.SecondWindow = QMainWindow()
        if self.sender() == self.file1Button:
            self.ui1 = Ui_SecondWindow()
            self.ui1.setupUi(self.SecondWindow, excelDir)
            self.SecondWindow.show()
        else:
            self.ui2 = Ui_SecondWindow()
            self.ui2.setupUi(self.SecondWindow, excelDir)
            self.SecondWindow.show()

    def changeSliders(self):
        if self.sender() == self.numOfContoursSlider:
            newlabel = 'Number of contours: ' + str(self.numOfContoursSlider.value())
            self.numOfContoursLabel.setText(newlabel)
            self.status['numOfContour'] = self.numOfContoursSlider.value()

        if self.sender() == self.colorIntensitySlider:
            newlabel = 'Color Intensity: ' + str(self.colorIntensitySlider.value())
            self.colorIntensityLabel.setText(newlabel)
            self.status['colorMapIntensity'] = self.colorIntensitySlider.value()/100.

        if self.sender() == self.contourLinesIntensitySlider:
            newlabel = 'Contour lines Intensity: ' + str(self.contourLinesIntensitySlider.value())
            self.contourLinesIntensityLabel.setText(newlabel)
            self.status['colorLinesIntensity'] = self.contourLinesIntensitySlider.value()/100.

        if self.auxvar:
            self.figure.clear()
            self.corr.plotFunction(**self.status)

    def changeStatus(self):

        # THIS function must be improved, so not all buttons are updated but only checking into the group that was called
        self.status['colorMap'] = self.colorMapBox.currentText()
        self.status['colorLines'] = self.contourLinesColorBox.currentText()

        if self.homoCorrButton.isChecked():
                self.status['corrType'] = 'homo'
        else:
                self.status['corrType'] = 'hetero'

        if self.hilbertTransformButton.isChecked():
                self.status['calcMethod'] = 'HT'
        else:
                self.status['calcMethod'] = 'FFT'

        if self.meanButton.isChecked():
                self.status['refSpectra'] = 'mean'
        elif self.initialButton.isChecked():
                self.status['refSpectra'] = 'ini'
        elif self.finalButton.isChecked():
                self.status['refSpectra'] = 'end'
        else:
                self.status['refSpectra'] = 'zero'

        if self.syncMainDiagButton.isChecked():
                self.status['syncDiag'] = 'main'
        else:
                self.status['syncDiag'] = 'anti'

        if self.asyncMainDiagButton.isChecked():
                self.status['asyncDiag'] = 'main'
        else:
                self.status['asyncDiag'] = 'anti'

        if self.increasingXbutton.isChecked():
                self.status['xAxis'] = 'increasing'
        else:
                self.status['xAxis'] = 'decreasing'

        if self.syncGraphOption.isChecked():
                self.status['shownGraph'] = 'sync'
        elif self.asyncGraphOption.isChecked():
                self.status['shownGraph'] = 'async'
        else:
                self.status['shownGraph'] = 'both'

        if self.auxvar:
            self.figure.clear()
            self.corr.plotFunction(**self.status)

    def plotButtonFunction(self):

        if ValidateExtension(self.type1, self.type2):

            # In case the data is stored in an Excel file, the sheet, row and columns are provided
            if hasattr(self, 'ui1') and self.type1 == "xlsx":
                location = [self.ui1.sheet, self.ui1.row, self.ui1.column, self.ui1.labeledColumns.isChecked()]
                self.filename1 += location

            if hasattr(self, 'ui2') and self.type2 == "xlsx":
                location = [self.ui2.sheet, self.ui2.row, self.ui2.column, self.ui2.labeledColumns.isChecked()]
                self.filename2 += location

            # creation of the object. If it has been created before with the same files, then don't create again
            if 'prev' not in locals():
                prev = ""  # this is only an initial value for the case that the variable prev didnt exist

            if prev != [self.filename1, self.filename2]:  # if it exists with the same name as before, then don't create the object again
                self.corr = twoDspecies(self.filename1, self.filename2, ref=self.status['refSpectra'], method=self.status['calcMethod'])
                prev = [self.filename1, self.filename2]
                self.auxvar = True


            # the correlation is recalculated
            self.corr.syn(method=self.status['calcMethod'])  # let the user decide
            self.corr.asyn(method=self.status['calcMethod'])  # let the user decide

            # once the ok button is pressed, the plot is generated
            if self.auxvar:
                self.corr.canvas_ = self.canvas
                self.corr.plotFunction(**self.status)

    def show3D(self):
        if self.auxvar:
            self.corr.plot3D()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

