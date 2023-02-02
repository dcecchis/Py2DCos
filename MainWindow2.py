import matplotlib as mpl
import matplotlib.pyplot as plt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QSlider
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from ErrorMessages import ValidateMethod, ValidateExtension
import scipy.interpolate as si
from twoDspecies import twoDspecies
from SecondWindow import Ui_SecondWindow
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import numpy as np
# import qdarktheme
import plotly.graph_objs as go

## List of line_color supported
color_list = ["navy", 'black', "white", "red", "lime", "blue", "yellow", "maroon", "olive",
              "green", "teal"]
## List of cmap supported
cmap_list = ['bwr', 'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu',
             'RdYlGn', 'Spectral', 'coolwarm', 'seismic']

### Default graphical parameters
default_graphic = {
        'homo_type': True,  # Check! because if it is set to False don't ask for the 2 file names
        'hilber_calc': True,
        'ref_spectra': 'initial', # 'mean' , 'zero' , 'initial' , 'final'
        'cmap': cmap_list[10],
        'numCont': 12,
        'diag1sync': True,
        'diag1async': False,
        'incX': False,
        'cmap_intensity': 1.0,
        'line_color': color_list[1],
        'lines_intensity': 0.6,
        'sync_async': 'both'  # 'sync' , 'async' , 'both'
    }

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1558, 890)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.optionsFrame = QtWidgets.QFrame(self.centralwidget)
        self.optionsFrame.setGeometry(QtCore.QRect(30, 10, 321, 820))
        self.optionsFrame.setFrameShape(QtWidgets.QFrame.Box)
        self.optionsFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.optionsFrame.setObjectName("optionsFrame")
        self.plotFrame1 = QtWidgets.QFrame(self.centralwidget)
        self.plotFrame1.setGeometry(QtCore.QRect(370, 10, 1161, 761))
        self.plotFrame1.setFrameShape(QtWidgets.QFrame.Box)
        self.plotFrame1.setFrameShadow(QtWidgets.QFrame.Raised)
        self.plotFrame1.setObjectName("plotFrame1")
        self.toolsFrame = QtWidgets.QFrame(self.centralwidget)
        self.toolsFrame.setGeometry(QtCore.QRect(451, 775, 800, 58))
        self.toolsFrame.setFrameShape(QtWidgets.QFrame.Box)
        self.toolsFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.toolsFrame.setObjectName("navFrame")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 955, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.triDbuttonFrame = QtWidgets.QFrame(self.centralwidget)
        self.triDbuttonFrame.setGeometry(QtCore.QRect(1300, 775, 90, 25))
        self.triDbuttonFrame.setFrameShape(QtWidgets.QFrame.Box)
        self.triDbuttonFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.triDbuttonFrame.setObjectName("3dFrame")

        # font used in text
        font = QtGui.QFont()
        font.setFamily("Yu Gothic UI Semibold")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)

        # Correlation type text
        self.CorrTypeLabel = QtWidgets.QLabel(self.optionsFrame)
        self.CorrTypeLabel.setGeometry(QtCore.QRect(10, 0, 161, 41))
        self.CorrTypeLabel.setFont(font)
        self.CorrTypeLabel.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.CorrTypeLabel.setWordWrap(False)
        self.CorrTypeLabel.setObjectName("label")

        # calculation method text
        self.label_calc = QtWidgets.QLabel(self.optionsFrame)
        self.label_calc.setGeometry(QtCore.QRect(10, 80, 190, 41))
        self.label_calc.setFont(font)
        self.label_calc.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_calc.setWordWrap(False)
        self.label_calc.setObjectName("label_calc")

        # Input text
        self.label_3 = QtWidgets.QLabel(self.optionsFrame)
        self.label_3.setGeometry(QtCore.QRect(10, 150, 181, 41))
        self.label_3.setFont(font)
        self.label_3.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_3.setWordWrap(False)
        self.label_3.setObjectName("label_3")

        # Reference Spectra Text
        self.RefSpectraLabel = QtWidgets.QLabel(self.optionsFrame)
        self.RefSpectraLabel.setGeometry(QtCore.QRect(10, 260, 181, 41))
        self.RefSpectraLabel.setFont(font)
        self.RefSpectraLabel.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.RefSpectraLabel.setWordWrap(False)
        self.RefSpectraLabel.setObjectName("label_5")

        # Graph Settings Text
        self.GraphSettingsLabel = QtWidgets.QLabel(self.optionsFrame)
        self.GraphSettingsLabel.setGeometry(QtCore.QRect(10, 430, 181, 41))
        self.GraphSettingsLabel.setFont(font)
        self.GraphSettingsLabel.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.GraphSettingsLabel.setWordWrap(False)
        self.GraphSettingsLabel.setObjectName("label_4")

        # text in settings
        self.NumofContlabel = QtWidgets.QLabel(self.optionsFrame)
        self.NumofContlabel.setGeometry(QtCore.QRect(30, 480, 141, 16))
        self.NumofContlabel.setObjectName("label_2")
        self.label_cmapInt = QtWidgets.QLabel(self.optionsFrame)
        self.label_cmapInt.setGeometry(QtCore.QRect(30, 575, 141, 16))
        self.label_cmapInt.setObjectName("label_cmapInt")
        self.label_linesInt = QtWidgets.QLabel(self.optionsFrame)
        self.label_linesInt.setGeometry(QtCore.QRect(30, 610, 141, 16))
        self.label_linesInt.setObjectName("label_linesInt")
        self.label_lineColor = QtWidgets.QLabel(self.optionsFrame)
        self.label_lineColor.setGeometry(QtCore.QRect(30, 540, 141, 16))
        self.label_lineColor.setObjectName("label_linesInt")
        self.label_cmap = QtWidgets.QLabel(self.optionsFrame)
        self.label_cmap.setGeometry(QtCore.QRect(30, 510, 141, 16))
        self.label_cmap.setObjectName("cmap_Label")
        self.label_diag = QtWidgets.QLabel(self.optionsFrame)
        self.label_diag.setGeometry(QtCore.QRect(100, 650, 141, 16))
        self.label_diag.setObjectName("label_diag")
        self.label_syncdiag = QtWidgets.QLabel(self.optionsFrame)
        self.label_syncdiag.setGeometry(QtCore.QRect(30, 670, 141, 16))
        self.label_syncdiag.setObjectName("labelsync_diag")
        self.label_asyncdiag = QtWidgets.QLabel(self.optionsFrame)
        self.label_asyncdiag.setGeometry(QtCore.QRect(30, 695, 141, 16))
        self.label_asyncdiag.setObjectName("labelasync_diag")
        self.label_diag2 = QtWidgets.QLabel(self.optionsFrame)
        self.label_diag2.setGeometry(QtCore.QRect(30, 730, 141, 16))
        self.label_diag2.setObjectName("label_diag2")

        # auxiliar variables needed
        self.auxvar = False  # used for avoiding bug if changing setting options before plotting
        self.heteroBool = not default_graphic['homo_type']  # for showing and hiding the 2nd upload widget
        self.filename1 = ""
        self.filename2 = ""
        self.type1 = ""
        self.type2 = ""

        # BUTTONS
        # Correlation type buttons
        self.HomoButton = QtWidgets.QRadioButton(self.optionsFrame, clicked=lambda: self.hideHeteroUpload())
        self.HomoButton.setGeometry(QtCore.QRect(10, 50, 131, 20))
        self.HomoButton.setObjectName("HomoButton")
        self.HomoButton.setChecked(not self.heteroBool)
        self.CorrTypeButtons = QtWidgets.QButtonGroup(MainWindow)
        self.CorrTypeButtons.setObjectName("CorrTypeButtons")
        self.CorrTypeButtons.addButton(self.HomoButton)
        self.HeteroButton = QtWidgets.QRadioButton(self.optionsFrame, clicked=lambda: self.showHeteroUpload())
        self.HeteroButton.setGeometry(QtCore.QRect(160, 50, 131, 20))
        self.HeteroButton.setObjectName("HeteroButton")
        self.HeteroButton.setChecked(self.heteroBool)
        self.CorrTypeButtons.addButton(self.HeteroButton)

        # Calculation method buttons
        self.HilbertButton = QtWidgets.QRadioButton(self.optionsFrame)
        self.HilbertButton.setGeometry(QtCore.QRect(10, 130, 125, 20))
        self.HilbertButton.setGeometry(QtCore.QRect(10, 130, 125, 20))
        self.HilbertButton.setObjectName("HilbertButton")
        self.HilbertButton.setText("Hilbert Transform")
        self.HilbertButton.setChecked(default_graphic['hilber_calc'])
        self.FFTButton = QtWidgets.QRadioButton(self.optionsFrame)
        self.FFTButton.setGeometry(QtCore.QRect(160, 130, 111, 20))
        self.FFTButton.setObjectName("FFTButton")
        self.FFTButton.setText("FFT")
        self.FFTButton.setChecked(not default_graphic['hilber_calc'])
        self.CalcMethodButtons = QtWidgets.QButtonGroup(MainWindow)
        self.CalcMethodButtons.setObjectName("CorrSpectraButtons")
        self.CalcMethodButtons.addButton(self.HilbertButton)
        self.CalcMethodButtons.addButton(self.FFTButton)
        self.CalcMethodButtons.setExclusive(True)

        # upload file 1 button
        self.upload1 = QtWidgets.QPushButton(self.optionsFrame)
        self.upload1.setGeometry(QtCore.QRect(20, 190, 250, 30))
        self.upload1.setObjectName("upload1")
        # connect upload buttons with function
        self.upload1.clicked.connect(self.pushButtonUpload1)

        # reference spectra buttons
        self.MeanButton = QtWidgets.QRadioButton(self.optionsFrame)
        self.MeanButton.setGeometry(QtCore.QRect(30, 310, 95, 20))
        self.MeanButton.setObjectName("MeanButton")
        self.MeanButton.setChecked(True if default_graphic['ref_spectra']=='mean' else False)
        self.buttonGroup = QtWidgets.QButtonGroup(MainWindow)
        self.buttonGroup.setObjectName("buttonGroup")
        self.buttonGroup.addButton(self.MeanButton)
        self.ZeroButton = QtWidgets.QRadioButton(self.optionsFrame)
        self.ZeroButton.setGeometry(QtCore.QRect(160, 310, 95, 20))
        self.ZeroButton.setObjectName("ZeroButton")
        self.ZeroButton.setChecked(True if default_graphic['ref_spectra']=='zero' else False)
        self.buttonGroup.addButton(self.ZeroButton)
        self.InitialButton = QtWidgets.QRadioButton(self.optionsFrame)
        self.InitialButton.setGeometry(QtCore.QRect(30, 340, 95, 20))
        self.InitialButton.setObjectName("InitialButton")
        self.InitialButton.setChecked(True if default_graphic['ref_spectra']=='initial' else False)
        self.buttonGroup.addButton(self.InitialButton)
        self.FinalButton = QtWidgets.QRadioButton(self.optionsFrame)
        self.FinalButton.setGeometry(QtCore.QRect(160, 340, 95, 20))
        self.FinalButton.setObjectName("FinalButton")
        self.FinalButton.setChecked(True if default_graphic['ref_spectra']=='final' else False)
        self.buttonGroup.addButton(self.FinalButton)

        # plot button
        self.PlotButton = QtWidgets.QPushButton(self.optionsFrame, clicked=lambda: self.okFun())
        self.PlotButton.setGeometry(QtCore.QRect(80, 380, 161, 51))
        self.PlotButton.setObjectName("PlotButton")

        # Slider for number of contours
        self.numContour = default_graphic['numCont']
        self.NumContourSlider = QSlider(Qt.Horizontal, self.optionsFrame)
        self.NumContourSlider.setGeometry(QtCore.QRect(170, 480, 113, 22))
        self.NumContourSlider.setMinimum(1)
        self.NumContourSlider.setMaximum(40)
        self.NumContourSlider.setValue(self.numContour)
        self.NumContourSlider.valueChanged.connect(self.numOfContours)
        self.sliderLabel = QtWidgets.QLabel(self.optionsFrame)
        self.sliderLabel.setGeometry(QtCore.QRect(226, 465, 113, 22))
        self.sliderLabel.setText(str(self.NumContourSlider.value()))

        # Color map combobox
        self.cmap = default_graphic['cmap']
        self.cmapBox = QtWidgets.QComboBox(self.optionsFrame)
        self.cmapBox.setGeometry(QtCore.QRect(170, 510, 113, 22))
        self.cmapBox.setObjectName("cmapBox")
        for cmap in cmap_list:
            self.cmapBox.addItem(cmap)
        self.cmapBox.activated[str].connect(self.ChangeCmap)
        self.cmapBox.setCurrentText(default_graphic['cmap'])

        # line color combo box
        self.linecolor = default_graphic['line_color']
        self.colorLineBox = QtWidgets.QComboBox(self.optionsFrame)
        self.colorLineBox.setGeometry(QtCore.QRect(170, 540, 113, 22))
        self.colorLineBox.setObjectName("colorLineBox")
        for color in color_list:
            self.colorLineBox.addItem(color)
        self.colorLineBox.activated[str].connect(self.changeColor)
        self.colorLineBox.setCurrentText(default_graphic['line_color'])

        # diagonals buttons
        self.diag1sync = default_graphic['diag1sync']
        self.diag1async = default_graphic['diag1async']
        self.diag1syncButton = QtWidgets.QRadioButton(self.optionsFrame)
        self.diag1syncButton.setGeometry(QtCore.QRect(110, 670, 141, 16))
        self.diag1syncButton.setObjectName("diag1SyncButton")
        self.diag1syncButton.setText("Main Diag")
        self.diag1syncButton.setChecked(self.diag1sync)
        self.diag1syncButton.clicked.connect(self.changeDiag)
        self.diag2syncButton = QtWidgets.QRadioButton(self.optionsFrame)
        self.diag2syncButton.setGeometry(QtCore.QRect(195, 670, 141, 16))
        self.diag2syncButton.setObjectName("diag2SyncButton")
        self.diag2syncButton.setText("Antidiag")
        self.diag2syncButton.setChecked(not self.diag1sync)
        self.diag2syncButton.clicked.connect(self.changeDiag)
        self.syncdiagButton = QtWidgets.QButtonGroup(MainWindow)
        self.syncdiagButton.setObjectName("diagSyncButton")
        self.syncdiagButton.addButton(self.diag1syncButton)
        self.syncdiagButton.addButton(self.diag2syncButton)
        self.syncdiagButton.setExclusive(True)
        self.diag1asyncButton = QtWidgets.QRadioButton(self.optionsFrame)
        self.diag1asyncButton.setGeometry(QtCore.QRect(110, 695, 141, 16))
        self.diag1asyncButton.setObjectName("diag1SyncButton")
        self.diag1asyncButton.setText("Main Diag")
        self.diag1asyncButton.setChecked(self.diag1async)
        self.diag1asyncButton.clicked.connect(self.changeDiag)
        self.diag2asyncButton = QtWidgets.QRadioButton(self.optionsFrame)
        self.diag2asyncButton.setGeometry(QtCore.QRect(195, 695, 141, 16))
        self.diag2asyncButton.setObjectName("diag2SyncButton")
        self.diag2asyncButton.setText("Antidiag")
        self.diag2asyncButton.setChecked(not self.diag1async)
        self.diag2asyncButton.clicked.connect(self.changeDiag)
        self.asyncdiagButton = QtWidgets.QButtonGroup(MainWindow)
        self.asyncdiagButton.setObjectName("diagAsyncButton")
        self.asyncdiagButton.addButton(self.diag1asyncButton)
        self.asyncdiagButton.addButton(self.diag2asyncButton)
        self.asyncdiagButton.setExclusive(True)
        
        # increasing or decreasing x buttons
        self.incX = default_graphic['incX']
        self.increasingX = QtWidgets.QRadioButton(self.optionsFrame)
        self.increasingX.setGeometry(QtCore.QRect(110, 730, 141, 16))
        self.increasingX.setObjectName("diag1SyncButton")
        self.increasingX.setText("Increasing")
        self.increasingX.setChecked(self.incX)
        self.increasingX.clicked.connect(self.changeXdir)
        self.decreasingX = QtWidgets.QRadioButton(self.optionsFrame)
        self.decreasingX.setGeometry(QtCore.QRect(195, 730, 141, 16))
        self.decreasingX.setObjectName("diag2SyncButton")
        self.decreasingX.setText("Decreasing")
        self.decreasingX.setChecked(not self.incX)
        self.decreasingX.clicked.connect(self.changeXdir)
        self.Xdir = QtWidgets.QButtonGroup(MainWindow)
        self.Xdir.setObjectName("diagAsyncButton")
        self.Xdir.addButton(self.increasingX)
        self.Xdir.addButton(self.decreasingX)
        self.Xdir.setExclusive(True)

        # color map intensity slider
        self.cmap_int = int(default_graphic['cmap_intensity']*100)  # default intensity in colormap
        self.cmapIntensitySlider = QSlider(Qt.Horizontal, self.optionsFrame)
        self.cmapIntensitySlider.setGeometry(QtCore.QRect(170, 575, 113, 22))
        self.cmapIntensitySlider.setMinimum(1)
        self.cmapIntensitySlider.setMaximum(100)
        self.cmapIntensitySlider.setValue(self.cmap_int)
        self.cmapIntensitySlider.valueChanged.connect(self.change_cmapintensity)
        self.cmapIntensityLabel = QtWidgets.QLabel(self.optionsFrame)
        self.cmapIntensityLabel.setGeometry(QtCore.QRect(226, 560, 113, 22))
        self.cmapIntensityLabel.setText(str(self.cmapIntensitySlider.value()))


        # lines intensity slider
        self.lines_int = int(default_graphic['lines_intensity']*100)
        self.LineIntensitySlider = QSlider(Qt.Horizontal, self.optionsFrame)
        self.LineIntensitySlider.setGeometry(QtCore.QRect(170, 610, 113, 22))
        self.LineIntensitySlider.setMinimum(1)
        self.LineIntensitySlider.setMaximum(100)
        self.LineIntensitySlider.setValue(self.lines_int)
        self.LineIntensitySlider.valueChanged.connect(self.change_linesintensity)
        self.lineIntensityLabel = QtWidgets.QLabel(self.optionsFrame)
        self.lineIntensityLabel.setGeometry(QtCore.QRect(226, 595, 113, 22))
        self.lineIntensityLabel.setText(str(self.LineIntensitySlider.value()))

        # buttons for sync async or both
        self.syncButton = QtWidgets.QRadioButton(self.optionsFrame)
        self.syncButton.setGeometry(QtCore.QRect(30, 780, 141, 16))
        self.syncButton.setObjectName("SyncButton")
        self.syncButton.setText("Sync")
        self.syncButton.clicked.connect(self.ChangeCmap)
        self.syncButton.setChecked(True if default_graphic['sync_async']=='sync' else False)
        self.asyncButton = QtWidgets.QRadioButton(self.optionsFrame)
        self.asyncButton.setGeometry(QtCore.QRect(110, 780, 141, 16))
        self.asyncButton.setObjectName("AsyncButton")
        self.asyncButton.setText("Async")
        self.asyncButton.clicked.connect(self.ChangeCmap)
        self.asyncButton.setChecked(True if default_graphic['sync_async']=='async' else False)
        self.bothButton = QtWidgets.QRadioButton(self.optionsFrame)
        self.bothButton.setGeometry(QtCore.QRect(190, 780, 141, 16))
        self.bothButton.setObjectName("bothButton")
        self.bothButton.setText("Both")
        self.bothButton.clicked.connect(self.ChangeCmap)
        self.bothButton.setChecked(True if default_graphic['sync_async']=='both' else False)
        self.graphButton = QtWidgets.QButtonGroup(MainWindow)
        self.graphButton.setObjectName("GraphButton")
        self.graphButton.addButton(self.syncButton)
        self.graphButton.addButton(self.asyncButton)
        self.graphButton.addButton(self.bothButton)
        self.graphButton.setExclusive(True)

        # 3D button
        self.show3Dbutton = QtWidgets.QPushButton(self.triDbuttonFrame, clicked=lambda: self.show3Dsync())
        # self.show3Dbutton.setGeometry(QtCore.QRect(1300, 775, 200, 58))
        self.show3Dbutton.setObjectName("3dPlotButton")

        '''
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 957, 26))
        self.menubar.setObjectName("menubar")
        self.menuTheme = QtWidgets.QMenu(self.menubar)
        self.menuTheme.setObjectName("menuTheme")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOriginal = QtWidgets.QAction(MainWindow)
        self.actionOriginal.setObjectName("actionOriginal")
        self.actionDark = QtWidgets.QAction(MainWindow)
        self.actionDark.setObjectName("actionDark")
        self.actionLight = QtWidgets.QAction(MainWindow)
        self.actionLight.setObjectName("actionLight")
        self.menuTheme.addAction(self.actionOriginal)
        self.menuTheme.addAction(self.actionDark)
        self.menuTheme.addAction(self.actionLight)
        self.menubar.addAction(self.menuTheme.menuAction())

        self.actionOriginal.triggered.connect(lambda: self.changeOriginal())
        self.actionDark.triggered.connect(lambda: self.changeDark())
        self.actionLight.triggered.connect(lambda: self.changeLight())

    def changeDark(self):
        # self.figure.set_facecolor("#202124")
        app.setStyleSheet(qdarktheme.load_stylesheet())


    def changeLight(self):
        # self.figure.set_facecolor("#f8f9fa")
        app.setStyleSheet(qdarktheme.load_stylesheet("light"))

    def changeOriginal(self):
        # self.figure.set_facecolor("#f0f0f0")
        app.setStyleSheet("QLineEdit { background-color: #f0f0f0 }")
        
        '''  # testing dark theme

        # Creation of canvas
        # Creating First Canvas for plotting
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.plotFrame1)
        self.horizontalLayout.setObjectName("PlottingLayout")
        self.figure = plt.figure()
        self.canvas1 = FigureCanvas(self.figure)
        self.figure.set_facecolor("#f0f0f0")
        self.horizontalLayout.addWidget(self.canvas1)
        self.toolbar = NavigationToolbar(self.canvas1, None)
        self.toolsLayout = QtWidgets.QHBoxLayout(self.toolsFrame)
        self.toolsLayout.addWidget(self.toolbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    # FUNCTIONS
    # this function changes the number of contours and the slider label
    def numOfContours(self, value):
        self.numContour = value
        self.sliderLabel.setText(str(value))

        if self.auxvar:
            if self.bothButton.isChecked():
                self.plotOnCanvas3(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)
            elif self.syncButton.isChecked():
                self.plotOnCanvas1(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)
            elif self.asyncButton.isChecked():
                self.plotOnCanvas2(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)

    # this function changes the line color and the text in the combo box
    def changeColor(self):
        self.linecolor = self.colorLineBox.currentText()

        if self.auxvar:
            if self.bothButton.isChecked():
                self.plotOnCanvas3(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)
            elif self.syncButton.isChecked():
                self.plotOnCanvas1(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)
            elif self.asyncButton.isChecked():
                self.plotOnCanvas2(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)

    # this functions changes the diagonals
    def changeDiag(self):
        if self.diag1syncButton.isChecked():
            self.diag1sync = True
        else:
            self.diag1sync = False

        if self.diag1asyncButton.isChecked():
            self.diag1async = True
        else:
            self.diag1async = False

        if self.auxvar:
            if self.bothButton.isChecked():
                self.plotOnCanvas3(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)
            elif self.syncButton.isChecked():
                self.plotOnCanvas1(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)
            elif self.asyncButton.isChecked():
                self.plotOnCanvas2(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)

    # this function changes the direction in x-axis
    def changeXdir(self):
        if self.increasingX.isChecked():
            self.incX = True
        else:
            self.incX = False

        if self.auxvar:
            if self.bothButton.isChecked():
                self.plotOnCanvas3(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)
            elif self.syncButton.isChecked():
                self.plotOnCanvas1(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)
            elif self.asyncButton.isChecked():
                self.plotOnCanvas2(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)

    # this function changes the color map and the text in combo box
    def ChangeCmap(self):
        self.cmap = self.cmapBox.currentText()

        if self.auxvar:
            if self.bothButton.isChecked():
                self.plotOnCanvas3(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)
            elif self.syncButton.isChecked():
                self.plotOnCanvas1(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)
            elif self.asyncButton.isChecked():
                self.plotOnCanvas2(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)

    # this function shows a second button for uploading file in case of heterocorrelation
    def showHeteroUpload(self):
        self.heteroBool = True

        self.upload2 = QtWidgets.QPushButton(self.optionsFrame)
        self.upload2.setGeometry(QtCore.QRect(20, 230, 250, 30))
        self.upload2.setObjectName("upload2")
        self.upload2.setText("Choose your file")
        self.upload2.show()
        self.upload2.clicked.connect(self.pushButtonUpload2)

    # this function hides the button for uploading a second file
    def hideHeteroUpload(self):
        if self.heteroBool:
            self.upload2.hide()

    # this function changes the color map intensity and the slider label
    def change_cmapintensity(self, value):
        self.cmap_int = value
        self.cmapIntensityLabel.setText(str(value))

        if self.auxvar:
            if self.bothButton.isChecked():
                self.plotOnCanvas3(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)
            elif self.syncButton.isChecked():
                self.plotOnCanvas1(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)
            elif self.asyncButton.isChecked():
                self.plotOnCanvas2(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)

    # this function changes the line intensity and the slider label
    def change_linesintensity(self, value):
        self.lines_int = value
        self.lineIntensityLabel.setText(str(value))

        if self.auxvar:
            if self.bothButton.isChecked():
                self.plotOnCanvas3(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)
            elif self.syncButton.isChecked():
                self.plotOnCanvas1(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)
            elif self.asyncButton.isChecked():
                self.plotOnCanvas2(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                   diag1async=self.diag1async, incX=self.incX,
                                   cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                   line_color=self.linecolor)

    # this function generates the plot once the type, method and reference are specified
    def okFun(self):

        self.ref = ""
        if self.MeanButton.isChecked():
            self.ref = "mean"
        elif self.ZeroButton.isChecked():
            self.ref = "zero"
        elif self.InitialButton.isChecked():
            self.ref = "ini"
        elif self.FinalButton.isChecked():
            self.ref = "end"

        self.method = ""
        if self.HilbertButton.isChecked():
            self.method = "HT"
        else:
            self.method = "FFT"


        if ValidateMethod(self.method) and ValidateExtension(self.type1, self.type2):
    
            # In case the data is stored in an Excel file, the sheet, row and columns are provided
            if hasattr(self, 'ui1') and self.type1 == "xlsx":
                location = [self.ui1.sheet, self.ui1.row, self.ui1.column]
                self.filename1 += location
            if hasattr(self, 'ui2') and self.type2 == "xlsx":
                location = [self.ui2.sheet, self.ui2.row, self.ui2.column]
                self.filename2 += location
    
    
            # creation of the object. If it has been created before with the same files, then don't create again
            if 'prev' not in locals():
                prev = ""  # this is only an initial value for the case that the variable prev didnt exist
    
            if prev != [self.filename1, self.filename2]:  # if it exists with the same name as before, then don't create the object again
                self.corr = twoDspecies(self.filename1, self.filename2, ref=self.ref)
                prev = [self.filename1, self.filename2]
                self.auxvar = True
    
    
            # the correlation is recalculated
            self.corr.syn()  # let the user decide
            self.corr.asyn()  # let the user decide
            
            # once the ok button is pressed, the plot is generated
            if self.auxvar:
                if self.bothButton.isChecked():
                    self.plotOnCanvas3(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                       diag1async=self.diag1async, incX=self.incX,
                                       cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                       line_color=self.linecolor)
                elif self.syncButton.isChecked():
                    self.plotOnCanvas1(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                       diag1async=self.diag1async, incX=self.incX,
                                       cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                       line_color=self.linecolor)
                elif self.asyncButton.isChecked():
                    self.plotOnCanvas2(cmap=self.cmap, numCont=self.numContour, diag1sync=self.diag1sync,
                                       diag1async=self.diag1async, incX=self.incX,
                                       cmap_intensity=self.cmap_int / 100, lines_intensity=self.lines_int / 100,
                                       line_color=self.linecolor)


    # PLOTTING FUNCTIONS, necessary because the plots still can't be directly extracted from the object
    def plotOnCanvas1(self, cmap=default_graphic['cmap'], numCont=default_graphic['numCont'], 
                            diag1sync=default_graphic['diag1sync'], diag1async=default_graphic['diag1async'],
                            incX=default_graphic['incX'], cmap_intensity=default_graphic['cmap_intensity'],
                            line_color=default_graphic['line_color'], lines_intensity=default_graphic['lines_intensity']):  # sync plot

        self.figure.clear()

        if incX:
            Xpoint = self.corr.asyncr.index
        else:
            Xpoint = self.corr.asyncr.index
        func = si.interp2d(Xpoint, self.corr.asyncr.columns, self.corr.asyncr.values)

        def fmt(x, y):
            z = np.take(func(x, y), 0)
            return 'x={x:.3f}  y={y:.3f}  z={z:.3f}'.format(x=x, y=y, z=z)

        gs = mpl.gridspec.GridSpec(3, 5, width_ratios=[2.5, 2, 5, 0.25, 2.25], height_ratios=[2, 7, 2], wspace=0.03,
                                   hspace=0.05)
        fontsize = 8
        # keys to name the panels
        keys = ['central', 'upper', 'lefter', 'lower']
        params = ['axis', 'which', 'bottom', 'top', 'right', 'left', 'labelbottom', 'labelleft', 'labeltop',
                  'labelright']
        # proportion of the grids, to be able to iterates
        indices = [[1, 2], [0, 2], [1, 1], [2, 2]]

        panel_tick_params = {clave: {} for clave in keys}
        for clave in keys:
            for param in params:
                if param in ['axis', 'which']:
                    panel_tick_params[clave][param] = 'both'
                else:
                    panel_tick_params[clave][param] = True if clave in ['central'] or param in ['bottom', 'top',
                                                                                                'right',
                                                                                                'left'] else False

        for clave in ['upper', 'lower']:
            panel_tick_params[clave]['labelleft'] = True  # labels left is on in upper and lower panels

        panel_tick_params['lefter']['labelbottom'] = True  # labels bottom is on in lefter panel

        panels = {}
        # Creating the panels. This is done just one
        for i, clave in enumerate(keys):
            j, k = indices[i]
            if indices[i] not in [[1, 2], [1, 1], [1, 3]]:
                panels[clave] = self.figure.add_subplot(gs[j, k], sharex=panels['central'])
            elif indices[i] == [1, 1]:
                panels[clave] = self.figure.add_subplot(gs[j, k], sharey=panels['central'])
            elif indices[i] == [1, 3]:
                panels[clave] = self.figure.add_subplot(gs[j, k], sharex=panels['central'], sharey=panels['central'])
            else:
                panels[clave] = self.figure.add_subplot(gs[j, k])

            panels[clave].tick_params(
                axis=panel_tick_params[clave]['axis'],  # changes apply to the x-axis
                which=panel_tick_params[clave]['which'],  # both major and minor ticks are affected
                bottom=panel_tick_params[clave]['bottom'],  # ticks along the bottom edge are off
                top=panel_tick_params[clave]['top'],  # ticks along the top edge are off
                right=panel_tick_params[clave]['right'],  # ticks along the right edge are off
                left=panel_tick_params[clave]['left'],  # ticks along the left edge are off
                labelbottom=panel_tick_params[clave]['labelbottom'],  # labels along the bottom edge are off
                labelleft=panel_tick_params[clave]['labelleft'],  # labels along the left edge are off
                labeltop=panel_tick_params[clave]['labeltop'],  # labels along the bottom edge are off
                labelright=panel_tick_params[clave]['labelright'])  # labels along the left edge are off

        # Setting particularly the lefter panel
        panels['lefter'].invert_xaxis()
        
        # Direction of X axis in central panel

        # Plotting the information...
        num_wave = self.corr.describe1.index

        data_trans = self.corr.describe1
        panels['upper'].plot(num_wave, data_trans['mean'], label='Mean')
        panels['upper'].fill_between(num_wave, data_trans['min'], data_trans['max'], alpha=0.3, label='min-max')
        panels['upper'].fill_between(num_wave, data_trans['25%'], data_trans['75%'], alpha=0.6, label='Q25-Q75')
        panels['upper'].legend(loc='best', fontsize=fontsize)
        panels['upper'].set_xlim(num_wave.min(), num_wave.max())

        num_wave = self.corr.describe2.index
        data_trans = self.corr.describe2
        panels['lefter'].plot(data_trans['mean'], num_wave, label='Mean')  ## Attention! The data is inverted
        panels['lefter'].fill_betweenx(num_wave, data_trans['min'], data_trans['max'], alpha=0.3, label='min-max')
        panels['lefter'].fill_betweenx(num_wave, data_trans['25%'], data_trans['75%'], alpha=0.6, label='Q25-Q75')
        panels['lefter'].legend(loc='best', fontsize=fontsize)
        panels['lefter'].set_ylim(num_wave.min(), num_wave.max())

        # Setting the central and lower panels

        data = self.corr.syncr.values
        
        num_wave = self.corr.syncr.index
        num_wave2 = self.corr.syncr.columns
        # This test only plot the diagonal of sync 2D corr
        panels['lower'].plot(num_wave, data.diagonal(0))
        panels['lower'].axhline(y=0., color='k', alpha=0.4)
        panels['lower'].set_xlim(num_wave.min(), num_wave.max())

        # breakpoint()    # for debugging
        zmin = data.min()
        zmax = data.max()

        imshow_kwargs = {
            'vmax': zmax,
            'vmin': zmin,
            'cmap': cmap,
            'extent': (num_wave[0], num_wave[-1], num_wave2[0], num_wave2[-1]),
        }
        imA = panels['central'].imshow(data[::-1,::], alpha=cmap_intensity, **imshow_kwargs)
        panels['central'].contour(num_wave, num_wave2, data, numCont, cmap=None, vmin=zmin, vmax=zmax,
                                  colors=line_color, alpha=lines_intensity)

        caxA = plt.axes( self.figure.add_subplot(gs[1,3]) )
        cbA = plt.colorbar(imA, cax=caxA)
        # self.figure.colorbar(panels['central'].contour(num_wave, num_wave2, data, numCont, cmap=cmap, vmin=zmin, vmax=zmax))

        # divider = make_axes_locatable(panels['central'])
        # cax = divider.append_axes('right', size='5%', pad=0.05)
        # self.figure.colorbar(panels['central'].contour(num_wave, num_wave2, data, numCont, cmap=cmap, vmin=zmin, vmax=zmax), cax=cax, orientation='vertical')

        # diagonals
        if diag1sync:
            panels['lower'].clear()
            panels['central'].plot(num_wave, num_wave2, color='k', linewidth=1., alpha=0.65)
            panels['lower'].plot(num_wave, data.diagonal(0))
            panels['lower'].axhline(y=0., color='k', alpha=0.4)
            panels['lower'].set_xlim(num_wave.min(), num_wave.max())
        else:
            panels['lower'].clear()
            panels['central'].plot(num_wave, num_wave2[::-1], color='k', linewidth=1., alpha=0.65)
            panels['lower'].plot(num_wave, np.fliplr(data).diagonal())
            panels['lower'].axhline(y=0., color='k', alpha=0.4)
            panels['lower'].set_xlim(num_wave.min(), num_wave.max())

        panels['central'].format_coord = fmt

        # plt.xlabel("X axis")
        # plt.ylabel("Y axis")
        panels['central'].set_xlim(num_wave.min(), num_wave.max())
        panels['central'].set_ylim(num_wave2.min(), num_wave2.max())

        if incX == False:
            panels['central'].invert_xaxis()

        gs.tight_layout(self.figure)

        self.canvas1.draw()

    def plotOnCanvas2(self, cmap=default_graphic['cmap'], numCont=default_graphic['numCont'], 
                        diag1sync=default_graphic['diag1sync'], diag1async=default_graphic['diag1async'],
                        incX=default_graphic['incX'], cmap_intensity=default_graphic['cmap_intensity'],
                        line_color=default_graphic['line_color'], lines_intensity=default_graphic['lines_intensity']):  # async plot
        # Canvas 2
        self.figure.clear()
        # self.canvas1.figure.tight_layout()

        # function for the display of Z values
        func = si.interp2d(self.corr.asyncr.index, self.corr.asyncr.columns, self.corr.asyncr.values)

        def fmt(x, y):
            z = np.take(func(x, y), 0)
            return 'x={x:.3f}  y={y:.3f}  z={z:.3f}'.format(x=x, y=y, z=z)

        gs = mpl.gridspec.GridSpec(3, 5, width_ratios=[2.5, 2, 5, 0.25, 2.25], height_ratios=[2, 7, 2], wspace=0.03,
                                   hspace=0.05)
        fontsize = 8
        # keys to name the panels
        keys = ['central', 'upper', 'lefter', 'lower']
        params = ['axis', 'which', 'bottom', 'top', 'right', 'left', 'labelbottom', 'labelleft', 'labeltop',
                  'labelright']
        # proportion of the grids, to be able to iterates
        indices = [[1, 2], [0, 2], [1, 1], [2, 2]]

        panel_tick_params = {clave: {} for clave in keys}
        for clave in keys:
            for param in params:
                if param in ['axis', 'which']:
                    panel_tick_params[clave][param] = 'both'
                else:
                    panel_tick_params[clave][param] = True if clave in ['central'] or param in ['bottom', 'top',
                                                                                                'right',
                                                                                                'left'] else False

        for clave in ['upper', 'lower']:
            panel_tick_params[clave]['labelleft'] = True  # labels left is on in upper and lower panels

        panel_tick_params['lefter']['labelbottom'] = True  # labels bottom is on in lefter panel

        panels = {}
        # Creating the panels. This is done just one
        for i, clave in enumerate(keys):
            j, k = indices[i]
            if indices[i] not in [[1, 2], [1, 1], [1, 3]]:
                panels[clave] = self.figure.add_subplot(gs[j, k], sharex=panels['central'])
            elif indices[i] == [1, 1]:
                panels[clave] = self.figure.add_subplot(gs[j, k], sharey=panels['central'])
            elif indices[i] == [1, 3]:
                panels[clave] = self.figure.add_subplot(gs[j, k], sharex=panels['central'], sharey=panels['central'])
            else:
                panels[clave] = self.figure.add_subplot(gs[j, k])

            panels[clave].tick_params(
                axis=panel_tick_params[clave]['axis'],  # changes apply to the x-axis
                which=panel_tick_params[clave]['which'],  # both major and minor ticks are affected
                bottom=panel_tick_params[clave]['bottom'],  # ticks along the bottom edge are off
                top=panel_tick_params[clave]['top'],  # ticks along the top edge are off
                right=panel_tick_params[clave]['right'],  # ticks along the right edge are off
                left=panel_tick_params[clave]['left'],  # ticks along the left edge are off
                labelbottom=panel_tick_params[clave]['labelbottom'],  # labels along the bottom edge are off
                labelleft=panel_tick_params[clave]['labelleft'],  # labels along the left edge are off
                labeltop=panel_tick_params[clave]['labeltop'],  # labels along the bottom edge are off
                labelright=panel_tick_params[clave]['labelright'])  # labels along the left edge are off
        # Setting particularly the lefter panel
        panels['lefter'].invert_xaxis()
        # panels['lefter'].invert_yaxis()

        # Plotting the information...
        # panels['upper'].plot(num_wave,spect)
        num_wave = self.corr.describe1.index
        data_trans = self.corr.describe1
        panels['upper'].plot(num_wave, data_trans['mean'], label='Mean')
        panels['upper'].fill_between(num_wave, data_trans['min'], data_trans['max'], alpha=0.3, label='min-max')
        panels['upper'].fill_between(num_wave, data_trans['25%'], data_trans['75%'], alpha=0.6, label='Q25-Q75')
        panels['upper'].legend(loc='best', fontsize=fontsize)
        panels['upper'].set_xlim(num_wave.min(), num_wave.max())

        num_wave = self.corr.describe2.index
        data_trans = self.corr.describe2
        panels['lefter'].plot(data_trans['mean'], num_wave, label='Mean')  ## Attention! The data is inverted
        panels['lefter'].fill_betweenx(num_wave, data_trans['min'], data_trans['max'], alpha=0.3, label='min-max')
        panels['lefter'].fill_betweenx(num_wave, data_trans['25%'], data_trans['75%'], alpha=0.6, label='Q25-Q75')
        panels['lefter'].legend(loc='best', fontsize=fontsize)
        panels['lefter'].set_ylim(num_wave.min(), num_wave.max())

        # Setting the central and lower panels
        data = self.corr.asyncr.values
        # data.flags(write = True)
        #data[abs(data)<1.E-16] = 0.
        num_wave = self.corr.asyncr.index
        num_wave2 = self.corr.asyncr.columns

        # This test only plot the diagonal of sync 2D corr
        #diagonal = np.flip(np.fliplr(data).diagonal(0))
        #.setflags(write=True)
        #diagonal[diagonal < 1E-15] = 0.
        #panels['lower'].plot(num_wave, diagonal)
        panels['lower'].plot(num_wave, np.flip(np.fliplr(data).diagonal(0)))
        panels['lower'].axhline(y=0., color='k', alpha=0.4)
        panels['lower'].set_xlim(num_wave.min(), num_wave.max())

        # breakpoint()    # for debugging
        zmin = data.min()
        zmax = data.max()

        imshow_kwargs = {
            'vmax': zmax,
            'vmin': zmin,
            'cmap': cmap,
            'extent': (num_wave[0], num_wave[-1], num_wave2[0], num_wave2[-1]),
        }
        imA = panels['central'].imshow(data[::-1,::], alpha=cmap_intensity, **imshow_kwargs)
        panels['central'].contour(num_wave, num_wave2, data, numCont, cmap=None, vmin=zmin, vmax=zmax,
                                  colors=line_color, alpha=lines_intensity)

        caxA = plt.axes( self.figure.add_subplot(gs[1,3]) )
        cbA = plt.colorbar(imA, cax=caxA)

        # Plotting the diagonal
        if diag1async:
            panels['lower'].clear()
            panels['central'].plot(num_wave, num_wave2, linewidth=1., color='k', alpha=0.65)
            panels['lower'].plot(num_wave, data.diagonal(0))
            panels['lower'].axhline(y=0., color='k', alpha=0.4)
            panels['lower'].set_xlim(num_wave.min(), num_wave.max())

        else:
            panels['lower'].clear()
            panels['central'].plot(num_wave, num_wave2[::-1], linewidth=1., color='k', alpha=0.65)
            panels['lower'].plot(num_wave, np.flip(np.fliplr(data).diagonal(0)))
            panels['lower'].axhline(y=0., color='k', alpha=0.4)
            panels['lower'].set_xlim(num_wave.min(), num_wave.max())

        panels['central'].format_coord = fmt

        # plt.xlabel("X axis")
        # plt.ylabel("Y axis")
        panels['central'].set_xlim(num_wave.min(), num_wave.max())
        panels['central'].set_ylim(num_wave2.min(), num_wave2.max())

        if incX == False:
            panels['central'].invert_xaxis()

        gs.tight_layout(self.figure)

        self.canvas1.draw()

    def plotOnCanvas3(self,cmap=default_graphic['cmap'], numCont=default_graphic['numCont'],
                            diag1sync=default_graphic['diag1sync'], diag1async=default_graphic['diag1async'],
                            incX=default_graphic['incX'], cmap_intensity=default_graphic['cmap_intensity'],
                            line_color=default_graphic['line_color'], lines_intensity=default_graphic['lines_intensity']):  # both for sync plot and async plot

        self.figure.clear()
        self.canvas1.figure.tight_layout()

        func1 = si.interp2d(self.corr.syncr.index, self.corr.syncr.columns, self.corr.syncr.values)
        func2 = si.interp2d(self.corr.asyncr.index, self.corr.asyncr.columns, self.corr.asyncr.values)

        def fmt1(x, y):
            z = np.take(func1(x, y), 0)
            return 'x={x:.3f}  y={y:.3f}  z={z:.3f}'.format(x=x, y=y, z=z)

        def fmt2(x, y):
            z = np.take(func2(x, y), 0)
            return 'x={x:.5f}  y={y:.5f}  z={z:.5f}'.format(x=x, y=y, z=z)

        gs = mpl.gridspec.GridSpec(3, 5, width_ratios=[2, 5, 0.25, 5, 0.25], height_ratios=[2, 7, 2], wspace=0.03, hspace=0.03)
        fontsize = 8
        # keys to name the panels
        keys = ['central', 'upper', 'lefter', 'lower', 'upper_right', 'right', 'lower_right']
        params = ['axis', 'which', 'bottom', 'top', 'right', 'left', 'labelbottom', 'labelleft', 'labeltop',
                  'labelright']
        # proportion of the grids, to be able to iterates
        indices = [[1, 1], [0, 1], [1, 0], [2, 1], [0, 3], [1, 3], [2, 3]]
        panel_tick_params = {clave: {} for clave in keys}
        for clave in keys:
            for param in params:
                if param in ['axis', 'which']:
                    panel_tick_params[clave][param] = 'both'
                else:
                    panel_tick_params[clave][param] = True if clave in ['central', 'right'] or param in ['bottom',
                                                                                                         'top', 'right',
                                                                                                         'left'] else False

        for clave in ['upper', 'lower']:
            panel_tick_params[clave]['labelleft'] = True  # labels left is on in upper and lower panels

        for clave in ['upper_right', 'lower_right']:
            panel_tick_params[clave]['labelright'] = True  # labels left is on in upper and lower panels

        panel_tick_params['lefter']['labelbottom'] = True  # labels bottom is on in lefter panel

        panel_tick_params['central']['labelright'] = False  # labels right is off in central panel

        panel_tick_params['right']['labelleft'] = False  # labels left is off in right panel

        panels = {}
        # Creating the panels. This is done just one
        for i, clave in enumerate(keys):
            j, k = indices[i]
            if indices[i] not in [[1, 1], [1, 0], [1, 3]]:
                panels[clave] = self.figure.add_subplot(gs[j, k], sharex=panels['central'])
            elif indices[i] == [1, 3]:
                panels[clave] = self.figure.add_subplot(gs[j, k], sharex=panels['central'], sharey=panels['central'])
            elif indices[i] == [1, 0]:
                panels[clave] = self.figure.add_subplot(gs[j, k], sharey=panels['central'])
            else:
                panels[clave] = self.figure.add_subplot(gs[j, k])

            panels[clave].tick_params(
                axis=panel_tick_params[clave]['axis'],  # changes apply to the x-axis
                which=panel_tick_params[clave]['which'],  # both major and minor ticks are affected
                bottom=panel_tick_params[clave]['bottom'],  # ticks along the bottom edge are off
                top=panel_tick_params[clave]['top'],  # ticks along the top edge are off
                right=panel_tick_params[clave]['right'],  # ticks along the right edge are off
                left=panel_tick_params[clave]['left'],  # ticks along the left edge are off
                labelbottom=panel_tick_params[clave]['labelbottom'],  # labels along the bottom edge are off
                labelleft=panel_tick_params[clave]['labelleft'],  # labels along the left edge are off
                labeltop=panel_tick_params[clave]['labeltop'],  # labels along the bottom edge are off
                labelright=panel_tick_params[clave]['labelright'])  # labels along the left edge are off
        # Setting particularly the lefter panel
        panels['lefter'].invert_xaxis()
        # panels['lefter'].invert_yaxis()

        # Plotting the information...
        # panels['upper'].plot(num_wave,spect)
        num_wave = self.corr.describe1.index
        data_trans = self.corr.describe1
        panels['upper'].plot(num_wave, data_trans['mean'], label='Mean')
        panels['upper'].fill_between(num_wave, data_trans['min'], data_trans['max'], alpha=0.3, label='min-max')
        panels['upper'].fill_between(num_wave, data_trans['25%'], data_trans['75%'], alpha=0.6, label='Q25-Q75')
        panels['upper'].legend(loc='best', fontsize=fontsize)
        panels['upper'].set_xlim(num_wave.min(), num_wave.max())

        panels['upper_right'].plot(num_wave, data_trans['mean'], label='Mean')
        panels['upper_right'].fill_between(num_wave, data_trans['min'], data_trans['max'], alpha=0.3,
                                           label='min-max')
        panels['upper_right'].fill_between(num_wave, data_trans['25%'], data_trans['75%'], alpha=0.6,
                                           label='Q25-Q75')
        panels['upper_right'].legend(loc='best', fontsize=fontsize)
        panels['upper_right'].set_xlim(num_wave.min(), num_wave.max())

        num_wave = self.corr.describe2.index
        data_trans = self.corr.describe2
        panels['lefter'].plot(data_trans['mean'], num_wave, label='Mean')  ## Attention! The data is inverted
        panels['lefter'].fill_betweenx(num_wave, data_trans['min'], data_trans['max'], alpha=0.3, label='min-max')
        panels['lefter'].fill_betweenx(num_wave, data_trans['25%'], data_trans['75%'], alpha=0.6, label='Q25-Q75')
        panels['lefter'].legend(loc='best', fontsize=fontsize)
        panels['lefter'].set_ylim(num_wave.min(), num_wave.max())

        # Setting the central and lower panels

        data = self.corr.syncr.values
        # data[abs(data) < 1.E-16] = 0.
        num_wave = self.corr.syncr.index
        num_wave2 = self.corr.syncr.columns
        # This test only plot the diagonal of sync 2D corr
        panels['lower'].plot(num_wave, data.diagonal(0))
        panels['lower'].axhline(y=0., color='k', alpha=0.4)
        panels['lower'].set_xlim(num_wave.min(), num_wave.max())

        # breakpoint()    # for debugging
        zmin = data.min()
        zmax = data.max()

        imshow_kwargs = {
            'vmax': zmax,
            'vmin': zmin,
            'cmap': cmap,
            'extent': (num_wave[0], num_wave[-1], num_wave2[0], num_wave2[-1]),
        }
        panels['central'].contour(num_wave, num_wave2, data, numCont, cmap=None, vmin=zmin, vmax=zmax,
                                  colors=line_color, alpha=lines_intensity)
        imS = panels['central'].imshow(data[::-1,::], alpha=cmap_intensity, **imshow_kwargs)
        caxS = plt.axes( self.figure.add_subplot(gs[1,2]) )
        # ax = self.figure.add_subplot(gs[1,2])
        """
        ax.tick_params(
            axis='both',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom=False,  # ticks along the bottom edge are off
            top=False,  # ticks along the top edge are off
            right=False,  # ticks along the right edge are off
            left=False,  # ticks along the left edge are off
            labelbottom=False,  # labels along the bottom edge are off
            labelleft=False,  # labels along the left edge are off
            labeltop=False,  # labels along the bottom edge are off
            labelright=False)  # labels along the left edge are off
        caxS = inset_axes(ax, 
               width="60%",  
               height="80%",  
               loc='center left',
               bbox_to_anchor=(0.05, 0.0, 1, 1),
               bbox_transform=ax.transAxes,
               borderpad=0.05
               )
        """
        cbS = plt.colorbar(imS, cax=caxS)
        # cb.ax.yaxis.set_tick_params(labelright=True)

        # diagonals
        if diag1sync:
            panels['lower'].clear()
            panels['central'].plot(num_wave, num_wave2, linewidth=1., color='k', alpha=0.65)
            panels['lower'].plot(num_wave, data.diagonal(0))
            panels['lower'].axhline(y=0., color='k', alpha=0.4)
            panels['lower'].set_xlim(num_wave.min(), num_wave.max())
        else:
            panels['lower'].clear()
            panels['central'].plot(num_wave, num_wave2[::-1], linewidth=1., color='k', alpha=0.65)
            panels['lower'].plot(num_wave, np.fliplr(data).diagonal())
            panels['lower'].axhline(y=0., color='k', alpha=0.4)
            panels['lower'].set_xlim(num_wave.min(), num_wave.max())

        # plt.xlabel("X axis")
        # plt.ylabel("Y axis")
        panels['central'].set_xlim(num_wave.min(), num_wave.max())
        panels['central'].set_ylim(num_wave2.min(), num_wave2.max())
        panels['central'].format_coord = fmt1

        # Setting the right and lower_right panels
        data = self.corr.asyncr.values
        #data[abs(data) < 1.E-16] = 0.
        num_wave = self.corr.asyncr.index
        num_wave2 = self.corr.asyncr.columns

        # This test only plot the diagonal of sync 2D corr
        panels['lower_right'].plot(num_wave, np.flip(np.fliplr(data).diagonal(0)))
        panels['lower_right'].axhline(y=0., color='k', alpha=0.4)
        panels['lower_right'].set_xlim(num_wave.min(), num_wave.max())

        # breakpoint()    # for debugging
        zmin = data.min()
        zmax = data.max()

        imshow_kwargs['vmax'] = zmax
        imshow_kwargs['vmin'] = zmin

        imA = panels['right'].imshow(data[::-1,::], alpha=cmap_intensity, **imshow_kwargs)
        panels['right'].contour(num_wave, num_wave2, data, numCont, cmap=None, vmin=zmin, vmax=zmax,
                                alpha=lines_intensity, colors=line_color)
        caxA = plt.axes( self.figure.add_subplot(gs[1,4]) )
        cbA = plt.colorbar(imA, cax=caxA)
        # cb.ax.yaxis.set_tick_params(labelright=True)


        if diag1async:
            panels['lower_right'].clear()
            panels['right'].plot(num_wave, num_wave2, linewidth=1., color='k', alpha=0.65)
            panels['lower_right'].plot(num_wave, data.diagonal(0))
            panels['lower_right'].axhline(y=0., color='k', alpha=0.4)
            panels['lower_right'].set_xlim(num_wave.min(), num_wave.max())

        else:
            panels['lower_right'].clear()
            panels['right'].plot(num_wave, num_wave2[::-1], linewidth=1., color='k', alpha=0.65)
            panels['lower_right'].plot(num_wave, np.flip(np.fliplr(data).diagonal(0)))
            panels['lower_right'].axhline(y=0., color='k', alpha=0.4)
            panels['lower_right'].set_xlim(num_wave.min(), num_wave.max())

        panels['right'].set_xlim(num_wave.min(), num_wave.max())
        panels['right'].set_ylim(num_wave2.min(), num_wave2.max())
        panels['right'].format_coord = fmt2

        if incX == False:
            panels['central'].invert_xaxis()

        gs.tight_layout(self.figure)
        # gs.subplots_adjust(left = 0.1, bottom = 0.1, right = 0.9, top = 0.9, wspace=0.4, hspace=0.4)

        self.canvas1.draw()

    def show3Dsync(self):
        fig = go.Figure(data=[go.Surface(x=self.corr.syncr.index, y=self.corr.syncr.columns, z=self.corr.syncr.values)])

        """
        fig.update_layout(title='Synchronous Spectra', autosize=False,
                          width=1000, height=1000,
                          margin=dict(l=65, r=50, b=65, t=90))
        """
        fig.update_layout(title='Synchronous Spectra',
                          margin=dict(l=65, r=50, b=65, t=90))

        fig.show()

        fig2 = go.Figure(
            data=[go.Surface(x=self.corr.asyncr.index, y=self.corr.asyncr.columns, z=self.corr.asyncr.values)])

        fig2.update_layout(title='Asynchronous Spectra',
                           margin=dict(l=65, r=50, b=65, t=90))
        """
        fig2.update_layout(title='Asynchronous Spectra', autosize=False,
                          width=1000, height=1000,
                          margin=dict(l=65, r=50, b=65, t=90))
        """
        fig2.show()

    def pushButtonUpload1(self):
        # open file dialog
        filename = QFileDialog.getOpenFileName(MainWindow, "Open File", "",
                                               "All Files (*);; Excel files (*.xlsx);; CSV files (*.csv);; txt files (*.txt)")
        if filename:
            word = str(filename[0])
            self.type1 = self.getType(word)
            lastSlash = word[::-1].find("/")
            self.upload1.setText(word[len(word) - lastSlash:])
            self.filename1 = [filename[0], self.type1]

            if self.type1 == "xlsx":
                self.OpenWindow1(self.filename1[0])

    def pushButtonUpload2(self):
        # open file dialog
        filename = QFileDialog.getOpenFileName(MainWindow, "Open File", "",
                                               "All Files (*);; Excel files (*.xlsx);; CSV files (*.csv);; txt files (*.txt)")
        if filename:
            word = str(filename[0])
            self.type2 = self.getType(word)
            lastSlash = word[::-1].find("/")
            self.upload2.setText(word[len(word) - lastSlash:])
            self.filename2 = [filename[0], self.type2]
            if self.type2 == "xlsx":
                self.OpenWindow2(self.filename2[0])

    def getType(self, word):
        c = word[::-1].find(".")
        return word[len(word) - c:]

    def OpenWindow1(self, excelDir):
        self.SecondWindow = QtWidgets.QMainWindow()
        self.ui1 = Ui_SecondWindow()
        self.ui1.setupUi(self.SecondWindow, excelDir)
        self.SecondWindow.show()

    def OpenWindow2(self, excelDir):
        self.SecondWindow = QtWidgets.QMainWindow()
        self.ui2 = Ui_SecondWindow()
        self.ui2.setupUi(self.SecondWindow, excelDir)
        self.SecondWindow.show()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.CorrTypeLabel.setText(_translate("MainWindow", "Correlation Type"))
        self.label_calc.setText(_translate("MainWindow", "Calculation Method"))
        self.HomoButton.setText(_translate("MainWindow", "Homocorrelation"))
        self.HeteroButton.setText(_translate("MainWindow", "Heterocorrelation"))
        # self.label_2.setText(_translate("MainWindow", "Correlation Spectra"))
        # self.SynButton.setText(_translate("MainWindow", "Synchronous"))
        # self.AsynButton.setText(_translate("MainWindow", "Asynchronous"))
        self.label_3.setText(_translate("MainWindow", "Input"))
        # self.upload1text.setText(_translate("MainWindow", "Choose your file"))
        self.upload1.setText(_translate("MainWindow", "Choose your file"))
        self.PlotButton.setText(_translate("MainWindow", "OK"))
        self.show3Dbutton.setText(_translate("MainWindow", "Show 3D"))
        self.GraphSettingsLabel.setText(_translate("MainWindow", "Graph Settings"))
        self.NumofContlabel.setText(_translate("MainWindow", "Number of Contours"))
        self.label_cmapInt.setText(_translate("MainWindow", "Color Intensity"))
        self.label_linesInt.setText(_translate("MainWindow", "Contour Lines Intensity"))
        self.label_lineColor.setText(_translate("MainWindow", "Contour Lines Color"))
        self.label_cmap.setText(_translate("MainWindow", "Color Map"))
        self.RefSpectraLabel.setText(_translate("MainWindow", "Reference Spectra"))
        self.label_diag.setText(_translate("MainWindow", "Diagonals"))
        self.label_diag2.setText(_translate("MainWindow", "X axis"))
        self.label_syncdiag.setText(_translate("MainWindow", "Sync: "))
        self.label_asyncdiag.setText(_translate("MainWindow", "Async: "))
        self.MeanButton.setText(_translate("MainWindow", "Mean"))
        self.ZeroButton.setText(_translate("MainWindow", "Zero"))
        self.InitialButton.setText(_translate("MainWindow", "Initial"))
        self.FinalButton.setText(_translate("MainWindow", "Final"))
        # self.menuTheme.setTitle(_translate("MainWindow", "Theme"))
        # self.actionOriginal.setText(_translate("MainWindow", "Original"))
        # self.actionDark.setText(_translate("MainWindow", "Dark"))
        # self.actionLight.setText(_translate("MainWindow", "Light"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
