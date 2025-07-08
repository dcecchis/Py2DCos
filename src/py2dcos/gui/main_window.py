import logging
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QMainWindow, QHBoxLayout, QVBoxLayout, QGridLayout, QWidget,
    QPushButton, QLabel, QRadioButton, QSizePolicy, QMessageBox, QSlider,
    QComboBox, QFileDialog, QButtonGroup, QSpacerItem, QCheckBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from py2dcos.gui.SecondWindow import Ui_SecondWindow
from py2dcos.config.resources import color_list, cmap_list, initial_status, locators
from py2dcos.controller.app_controller import AppController
from py2dcos.plotting.correlation_plot import CorrelationPlotter

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants
MIN_CONTOURS = 1
MAX_CONTOURS = 40
MIN_INTENSITY = 0
MAX_INTENSITY = 100
MIN_LINES_INTENSITY = 0
MAX_LINES_INTENSITY = 100
MIN_GAUSSIAN = 0
MAX_GAUSSIAN = 5

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Py2DCoS")
        self.setup_ui()
        self._init_variables()
        self.setup_signals()
        self.setup_defaults()
        self.controller = AppController()

    def _init_variables(self):
        self.prev = None
        self.plot_ready = False  # used for avoiding bug if changing setting options before plotting
        self.filename1 = ""
        self.filename2 = ""
        self.format1 = ""
        self.format2 = ""
        self.status = initial_status.copy()

    def setup_ui(self):
        # central widget, layouts and UI components
        self.central_widget = QWidget()
        self.central_widget.setMinimumSize(QSize(600, 400))
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)  # Main Layout, horizontal
        self.create_left_layout()
        self.create_right_layout()

    def create_left_layout(self):
        self.left_layout = QVBoxLayout()
        self.main_layout.addLayout(self.left_layout, 1)
        self.left_layout.setAlignment(Qt.AlignTop)
        spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.create_correlation_type_section(spacer)
        #self.create_calculation_method_section(spacer)
        self.create_input_files_section(spacer)
        self.create_data_treatment_section(spacer)
        self.create_reference_spectra_section(spacer)
        self.create_graph_settings_section(spacer)
        self.create_diagonals_axes_section(spacer)
        self.create_shown_graph_section(spacer)
        self.left_layout.addItem(spacer)
        self.create_plot_button(spacer)

    def create_right_layout(self):
        self.right_layout = QVBoxLayout()
        self.figure = plt.figure()
        self.figure.set_facecolor("#f0f0f0")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.right_layout.addWidget(self.canvas)

        self.toolbar_layout = QHBoxLayout()
        self.right_layout.addLayout(self.toolbar_layout)
        self.toolbar = NavigationToolbar(self.canvas, None)
        self.tridimensional_projection_button = QPushButton("Show 3D Plot")
        self.toolbar_layout.addWidget(self.toolbar, alignment=Qt.AlignRight)
        self.toolbar_layout.addWidget(self.tridimensional_projection_button, alignment=Qt.AlignLeft)

        self.main_layout.addLayout(self.right_layout, 5)


    def create_correlation_type_section(self, spacer):
        # Section for choosing correlation type
        self.corr_type_layout = QVBoxLayout()
        corr_type_label = QLabel("Correlation Type")
        corr_type_label.setFont(self.get_font_title())
        self.corr_type_layout.addWidget(corr_type_label, alignment=Qt.AlignCenter)
        self.corr_type_buttons_layout = QHBoxLayout()
        self.homo_corr_button = QRadioButton("Homocorrelation")
        self.homo_corr_button.setFont(self.get_font_text())
        self.hetero_corr_button = QRadioButton("Heterocorrelation")
        self.hetero_corr_button.setFont(self.get_font_text())
        self.corr_type_buttons_layout.addWidget(self.homo_corr_button)
        self.corr_type_buttons_layout.addWidget(self.hetero_corr_button)
        self.corr_type_layout.addLayout(self.corr_type_buttons_layout)
        self.left_layout.addLayout(self.corr_type_layout)
        self.left_layout.addItem(spacer)

    def create_calculation_method_section(self, spacer):
        # Section for calculation method
        self.calc_method_layout = QVBoxLayout()
        self.calc_method_label = QLabel("Calculation Method")
        self.calc_method_label.setFont(self.get_font_title())
        self.calc_method_layout.addWidget(self.calc_method_label, alignment=Qt.AlignCenter)
        self.calc_method_buttons_layout = QHBoxLayout()
        self.hilbert_transform_button = QRadioButton("Hilbert Transform")
        self.hilbert_transform_button.setFont(self.get_font_text())
        self.fft_button = QRadioButton("FFT")
        self.fft_button.setFont(self.get_font_text())
        self.calc_method_buttons_layout.addWidget(self.hilbert_transform_button)
        self.calc_method_buttons_layout.addWidget(self.fft_button)
        self.calc_method_layout.addLayout(self.calc_method_buttons_layout)
        self.left_layout.addLayout(self.calc_method_layout)
        self.left_layout.addItem(spacer)

    def create_input_files_section(self, spacer):
        # Section for selecting input files
        self.input_files_layout = QVBoxLayout()
        input_files_label = QLabel("Input")
        input_files_label.setFont(self.get_font_title())
        self.input_files_layout.addWidget(input_files_label, alignment=Qt.AlignCenter)
        self.file1_button = QPushButton("Choose your File")
        self.file1_button.setMinimumSize(250, 30)
        self.file1_button.setFont(self.get_font_text())
        self.input_files_layout.addWidget(self.file1_button)
        self.file2_button = QPushButton("Choose your file")
        self.file2_button.setMinimumSize(250, 30)
        self.file2_button.setFont(self.get_font_text())
        self.input_files_layout.addWidget(self.file2_button)
        self.file2_button.hide()
        self.left_layout.addLayout(self.input_files_layout)
        self.left_layout.addItem(spacer)

    def create_data_treatment_section(self, spacer):
        # Section for selecting input files
        self.data_treatment_layout = QVBoxLayout()
        data_treatment_label = QLabel("Data Treatment")
        data_treatment_label.setFont(self.get_font_title())
        self.data_treatment_layout.addWidget(data_treatment_label, alignment=Qt.AlignCenter)

        self.data_treatment_grid_layout = QGridLayout()

        self.pca_reconstruction_components_label = QLabel("Components for PCA reconstruction")
        self.pca_reconstruction_components_label.setFont(self.get_font_text())
        self.data_treatment_grid_layout.addWidget(self.pca_reconstruction_components_label, 0, 0, alignment=Qt.AlignCenter)

        self.pca_reconstruction_components_combobox = QComboBox()
        self.pca_reconstruction_components_combobox.setFont(self.get_font_text())
        for i in range(0, 9):
            self.pca_reconstruction_components_combobox.addItem(str(i))
        self.data_treatment_grid_layout.addWidget(self.pca_reconstruction_components_combobox, 0, 1)

        self.gaussian_filter_slider = QSlider(Qt.Horizontal)
        self.gaussian_filter_slider.setMinimum(MIN_GAUSSIAN)
        self.gaussian_filter_slider.setMaximum(MAX_GAUSSIAN)
        self.gaussian_filter_slider.setValue(0)
        self.data_treatment_grid_layout.addWidget(self.gaussian_filter_slider, 1, 1)

        self.gaussian_filter_label = QLabel(f"Gaussian Smoothing: {self.gaussian_filter_slider.value()}")
        self.gaussian_filter_label.setFont(self.get_font_text())
        self.data_treatment_grid_layout.addWidget(self.gaussian_filter_label, 1, 0, alignment=Qt.AlignCenter)

        self.node_attenuation_label = QLabel("Apply Node Attenuation Filter")
        self.node_attenuation_label.setFont(self.get_font_text())
        self.data_treatment_grid_layout.addWidget(self.node_attenuation_label, 2, 0, alignment=Qt.AlignCenter)

        self.node_attenuation_checkbox = QCheckBox()
        self.node_attenuation_checkbox.setChecked(False)
        self.data_treatment_grid_layout.addWidget(self.node_attenuation_checkbox, 2, 1, alignment=Qt.AlignCenter)

        self.data_treatment_layout.addLayout(self.data_treatment_grid_layout)
        self.left_layout.addLayout(self.data_treatment_layout)
        self.left_layout.addItem(spacer)

    def create_reference_spectra_section(self, spacer):
        # Section for reference spectra selection
        self.reference_spectra_layout = QVBoxLayout()
        reference_spectra_label = QLabel("Reference Spectra")
        reference_spectra_label.setFont(self.get_font_title())
        self.reference_spectra_layout.addWidget(reference_spectra_label, alignment=Qt.AlignCenter)
        self.reference_spectra_buttons_layout = QGridLayout()
        self.mean_button = QRadioButton("Mean")
        self.mean_button.setFont(self.get_font_text())
        self.zero_button = QRadioButton("Zero")
        self.zero_button.setFont(self.get_font_text())
        self.initial_button = QRadioButton("Initial")
        self.initial_button.setFont(self.get_font_text())
        self.final_button = QRadioButton("Final")
        self.final_button.setFont(self.get_font_text())
        self.reference_spectra_buttons_layout.addWidget(self.mean_button, 0, 0)
        self.reference_spectra_buttons_layout.addWidget(self.zero_button, 0, 1)
        self.reference_spectra_buttons_layout.addWidget(self.initial_button, 1, 0)
        self.reference_spectra_buttons_layout.addWidget(self.final_button, 1, 1)
        self.reference_spectra_layout.addLayout(self.reference_spectra_buttons_layout)
        self.left_layout.addLayout(self.reference_spectra_layout)
        self.left_layout.addItem(spacer)

    def create_graph_settings_section(self, spacer):
        # Section for graph settings
        self.graph_settings_layout = QVBoxLayout()
        graph_settings_label = QLabel("Graph Settings")
        graph_settings_label.setFont(self.get_font_title())
        self.graph_settings_layout.addWidget(graph_settings_label, alignment=Qt.AlignCenter)
        self.graph_settings_grid = QGridLayout()
        # Number of contours slider
        self.num_of_contours_slider = QSlider(Qt.Horizontal)
        self.num_of_contours_slider.setMinimum(MIN_CONTOURS)
        self.num_of_contours_slider.setMaximum(MAX_CONTOURS)
        self.num_of_contours_slider.setValue(6)
        self.graph_settings_grid.addWidget(self.num_of_contours_slider, 0, 1)
        self.num_of_contours_label = QLabel(f"Number of Contours: {self.num_of_contours_slider.value()}")
        self.num_of_contours_label.setFont(self.get_font_text())
        self.graph_settings_grid.addWidget(self.num_of_contours_label, 0, 0)
        # Locator combo box
        self.locator_label = QLabel("Locator")
        self.locator_label.setFont(self.get_font_text())
        self.graph_settings_grid.addWidget(self.locator_label, 1, 0)
        self.locator_box = QComboBox()
        self.locator_box.setFont(self.get_font_text())
        for locator in locators:
            self.locator_box.addItem(locator)
        self.graph_settings_grid.addWidget(self.locator_box, 1, 1)
        # Color map combo box
        self.color_map_label = QLabel("Color Map")
        self.color_map_label.setFont(self.get_font_text())
        self.graph_settings_grid.addWidget(self.color_map_label, 2, 0)
        self.color_map_box = QComboBox()
        self.color_map_box.setFont(self.get_font_text())
        for cmap in cmap_list:
            self.color_map_box.addItem(cmap)
        self.graph_settings_grid.addWidget(self.color_map_box, 2, 1)
        # Contour lines color combo box
        self.contour_lines_color_label = QLabel("Contour Lines Color")
        self.contour_lines_color_label.setFont(self.get_font_text())
        self.graph_settings_grid.addWidget(self.contour_lines_color_label, 3, 0)
        self.contour_lines_color_box = QComboBox()
        self.contour_lines_color_box.setFont(self.get_font_text())
        for color in color_list:
            self.contour_lines_color_box.addItem(color)
        self.graph_settings_grid.addWidget(self.contour_lines_color_box, 3, 1)
        # Color intensity slider
        self.color_intensity_slider = QSlider(Qt.Horizontal)
        self.color_intensity_slider.setMinimum(MIN_INTENSITY)
        self.color_intensity_slider.setMaximum(MAX_INTENSITY)
        self.color_intensity_slider.setValue(100)
        self.graph_settings_grid.addWidget(self.color_intensity_slider, 4, 1)
        self.color_intensity_label = QLabel(f"Color Intensity: {self.color_intensity_slider.value()}")
        self.color_intensity_label.setFont(self.get_font_text())
        self.graph_settings_grid.addWidget(self.color_intensity_label, 4, 0)
        # Contour lines intensity slider
        self.contour_lines_intensity_slider = QSlider(Qt.Horizontal)
        self.contour_lines_intensity_slider.setMinimum(MIN_LINES_INTENSITY)
        self.contour_lines_intensity_slider.setMaximum(MAX_LINES_INTENSITY)
        self.contour_lines_intensity_slider.setValue(60)
        self.graph_settings_grid.addWidget(self.contour_lines_intensity_slider, 5, 1)
        self.contour_lines_intensity_label = QLabel(
            f"Contour Lines Intensity: {self.contour_lines_intensity_slider.value()}")
        self.contour_lines_intensity_label.setFont(self.get_font_text())
        self.graph_settings_grid.addWidget(self.contour_lines_intensity_label, 5, 0)
        self.graph_settings_layout.addLayout(self.graph_settings_grid)
        self.left_layout.addLayout(self.graph_settings_layout)
        self.left_layout.addItem(spacer)

    def create_diagonals_axes_section(self, spacer):
        # Section for diagonals and axes options
        self.diagonals_axes_layout = QVBoxLayout()
        diagonals_axes_label = QLabel("Diagonals and Axes")
        diagonals_axes_label.setFont(self.get_font_title())
        self.diagonals_axes_layout.addWidget(diagonals_axes_label, alignment=Qt.AlignCenter)
        self.diagonals_axes_grid = QGridLayout()
        self.sync_diag_label = QLabel("Sync: ")
        self.sync_diag_label.setFont(self.get_font_text())
        self.async_diag_label = QLabel("Async: ")
        self.async_diag_label.setFont(self.get_font_text())
        self.x_axis_label = QLabel("X Axis:")
        self.x_axis_label.setFont(self.get_font_text())
        self.sync_main_diag_button = QRadioButton("Main Diag")
        self.sync_main_diag_button.setFont(self.get_font_text())
        self.sync_antidiag_button = QRadioButton("Antidiag")
        self.sync_antidiag_button.setFont(self.get_font_text())
        self.async_main_diag_button = QRadioButton("Main Diag")
        self.async_main_diag_button.setFont(self.get_font_text())
        self.async_antidiag_button = QRadioButton("Antidiag")
        self.async_antidiag_button.setFont(self.get_font_text())
        self.increasing_x_button = QRadioButton("Increasing")
        self.increasing_x_button.setFont(self.get_font_text())
        self.decreasing_x_button = QRadioButton("Decreasing")
        self.decreasing_x_button.setFont(self.get_font_text())
        self.diagonals_axes_grid.addWidget(self.sync_diag_label, 0, 0)
        self.diagonals_axes_grid.addWidget(self.sync_main_diag_button, 0, 1)
        self.diagonals_axes_grid.addWidget(self.sync_antidiag_button, 0, 2)
        self.diagonals_axes_grid.addWidget(self.async_diag_label, 1, 0)
        self.diagonals_axes_grid.addWidget(self.async_main_diag_button, 1, 1)
        self.diagonals_axes_grid.addWidget(self.async_antidiag_button, 1, 2)
        self.diagonals_axes_grid.addWidget(self.x_axis_label, 2, 0)
        self.diagonals_axes_grid.addWidget(self.increasing_x_button, 2, 1)
        self.diagonals_axes_grid.addWidget(self.decreasing_x_button, 2, 2)
        self.diagonals_axes_layout.addLayout(self.diagonals_axes_grid)
        self.left_layout.addLayout(self.diagonals_axes_layout)
        self.left_layout.addItem(spacer)

    def create_shown_graph_section(self, spacer):
        # Section for choosing which graph to display
        self.shown_graph_layout = QVBoxLayout()
        shown_graph_label = QLabel("Shown Graph")
        shown_graph_label.setFont(self.get_font_title())
        self.shown_graph_layout.addWidget(shown_graph_label, alignment=Qt.AlignCenter)

        self.shown_graph_buttons_layout = QHBoxLayout()
        self.sync_graph_option = QRadioButton("Sync")
        self.sync_graph_option.setFont(self.get_font_text())
        self.async_graph_option = QRadioButton("Async")
        self.async_graph_option.setFont(self.get_font_text())
        self.both_graph_option = QRadioButton("Both")
        self.both_graph_option.setFont(self.get_font_text())
        self.shown_graph_buttons_layout.addWidget(self.sync_graph_option)
        self.shown_graph_buttons_layout.addWidget(self.async_graph_option)
        self.shown_graph_buttons_layout.addWidget(self.both_graph_option)
        self.shown_graph_layout.addLayout(self.shown_graph_buttons_layout)

        self.peaks_signs_button_layout = QHBoxLayout()
        self.positive_signs_option = QRadioButton("Positives")
        self.positive_signs_option.setFont(self.get_font_text())
        self.negative_signs_option = QRadioButton("Negatives")
        self.negative_signs_option.setFont(self.get_font_text())
        self.all_signs_option = QRadioButton("All")
        self.all_signs_option.setFont(self.get_font_text())
        self.peaks_signs_button_layout.addWidget(self.positive_signs_option)
        self.peaks_signs_button_layout.addWidget(self.negative_signs_option)
        self.peaks_signs_button_layout.addWidget(self.all_signs_option)
        self.shown_graph_layout.addLayout(self.peaks_signs_button_layout)

        self.left_layout.addLayout(self.shown_graph_layout)
        self.left_layout.addItem(spacer)

    def create_plot_button(self, spacer):
        self.plot_button = QPushButton("Plot")
        self.plot_button.setFont(self.get_font_title())
        self.plot_button.setMaximumSize(250, 50)
        self.plot_button.setMinimumSize(250, 50)
        self.left_layout.addWidget(self.plot_button, alignment=Qt.AlignHCenter)
        self.left_layout.addItem(spacer)

    def get_font_title(self):
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        return font

    def get_font_text(self):
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        return font

    def setup_signal_groups(self):
        # Create button groups to ensure mutual exclusivity
        self.corr_type_group = QButtonGroup()
        self.corr_type_group.addButton(self.homo_corr_button)
        self.corr_type_group.addButton(self.hetero_corr_button)
        self.corr_type_group.setExclusive(True)

        # self.calc_method_group = QButtonGroup()
        # self.calc_method_group.addButton(self.hilbert_transform_button)
        # self.calc_method_group.addButton(self.fft_button)
        # self.calc_method_group.setExclusive(True)

        self.input_files_group = QButtonGroup()
        self.input_files_group.addButton(self.file1_button)
        self.input_files_group.addButton(self.file2_button)

        self.reference_spectra_group = QButtonGroup()
        self.reference_spectra_group.addButton(self.mean_button)
        self.reference_spectra_group.addButton(self.zero_button)
        self.reference_spectra_group.addButton(self.initial_button)
        self.reference_spectra_group.addButton(self.final_button)
        self.reference_spectra_group.setExclusive(True)

        self.sync_diagonals_group = QButtonGroup()
        self.sync_diagonals_group.addButton(self.sync_main_diag_button)
        self.sync_diagonals_group.addButton(self.sync_antidiag_button)
        self.sync_diagonals_group.setExclusive(True)

        self.async_diagonals_group = QButtonGroup()
        self.async_diagonals_group.addButton(self.async_main_diag_button)
        self.async_diagonals_group.addButton(self.async_antidiag_button)
        self.async_diagonals_group.setExclusive(True)

        self.x_axis_group = QButtonGroup()
        self.x_axis_group.addButton(self.increasing_x_button)
        self.x_axis_group.addButton(self.decreasing_x_button)
        self.x_axis_group.setExclusive(True)

        self.shown_graph_group = QButtonGroup()
        self.shown_graph_group.addButton(self.sync_graph_option)
        self.shown_graph_group.addButton(self.async_graph_option)
        self.shown_graph_group.addButton(self.both_graph_option)
        self.shown_graph_group.setExclusive(True)

        self.peaks_signs_group = QButtonGroup()
        self.peaks_signs_group.addButton(self.positive_signs_option)
        self.peaks_signs_group.addButton(self.negative_signs_option)
        self.peaks_signs_group.addButton(self.all_signs_option)
        self.peaks_signs_group.setExclusive(True)

    def setup_signals(self):
        # First, set up button groups
        self.setup_signal_groups()
        # Connect UI signals to slots
        self.node_attenuation_checkbox.clicked.connect(self.change_status)
        self.homo_corr_button.clicked.connect(self.change_hetero_upload)
        self.hetero_corr_button.clicked.connect(self.change_hetero_upload)
        self.pca_reconstruction_components_combobox.activated[str].connect(self.change_status)
        self.file1_button.clicked.connect(self.upload_file)
        self.file2_button.clicked.connect(self.upload_file)
        # self.pca_checkbox.clicked.connect(self.toggle_pca_component)
        self.num_of_contours_slider.valueChanged.connect(self.update_slider_labels)
        self.num_of_contours_slider.sliderReleased.connect(self.change_sliders)
        self.color_intensity_slider.valueChanged.connect(self.update_slider_labels)
        self.color_intensity_slider.sliderReleased.connect(self.change_sliders)
        self.gaussian_filter_slider.valueChanged.connect(self.update_slider_labels)
        self.gaussian_filter_slider.sliderReleased.connect(self.change_sliders)
        self.contour_lines_intensity_slider.valueChanged.connect(self.update_slider_labels)
        self.contour_lines_intensity_slider.sliderReleased.connect(self.change_sliders)

        self.corr_type_group.buttonClicked.connect(self.change_status)
        self.reference_spectra_group.buttonClicked.connect(self.change_status)
        # self.calc_method_group.buttonClicked.connect(self.change_status)
        self.sync_diagonals_group.buttonClicked.connect(self.change_status)
        self.async_diagonals_group.buttonClicked.connect(self.change_status)
        self.x_axis_group.buttonClicked.connect(self.change_status)
        self.shown_graph_group.buttonClicked.connect(self.change_status)
        self.peaks_signs_group.buttonClicked.connect(self.change_status)
        self.color_map_box.activated[str].connect(self.change_status)
        self.locator_box.activated[str].connect(self.change_status)
        self.contour_lines_color_box.activated[str].connect(self.change_status)
        self.plot_button.clicked.connect(self.plot_button_function)
        self.tridimensional_projection_button.clicked.connect(self.plot_tridimensional)

    def setup_defaults(self):
        # Set default state for controls
        self.homo_corr_button.setChecked(True)
        # self.hilbert_transform_button.setChecked(True)
        self.initial_button.setChecked(True)
        self.locator_box.setCurrentText("linear")
        self.color_map_box.setCurrentText("coolwarm")
        self.contour_lines_color_box.setCurrentText("black")
        self.sync_main_diag_button.setChecked(True)
        self.async_main_diag_button.setChecked(True)
        self.decreasing_x_button.setChecked(True)
        self.both_graph_option.setChecked(True)
        self.all_signs_option.setChecked(True)
        # self.status["figure"] = self.figure

    def upload_file(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Open File", "",
                "All Files (*);; Excel files (*.xlsx);; CSV files (*.csv);; txt files (*.txt)"
            )
            if not filename:
                return
            name = filename.rsplit("/", 1)[-1]
            if not name:
                raise ValueError("File name could not be retrieved")
            format_ = name.rsplit(".", 1)[-1]
            if self.sender() == self.file1_button:
                self.file1_button.setText(name)
                self.filename1 = [filename, format_]
                self.format1 = format_
                if format_ == "xlsx":
                    self.open_second_window(filename)
            else:
                self.file2_button.setText(name)
                self.filename2 = [filename, format_]
                self.format2 = format_
                if format_ == "xlsx":
                    self.open_second_window(filename)
        except Exception as e:
            QMessageBox.critical(self, "Error Loading File", f"An error occurred: {str(e)}")

    def change_hetero_upload(self):
        self.file2_button.setVisible(self.sender() != self.homo_corr_button)

    def open_second_window(self, excel_dir):
        self.second_window = QMainWindow()
        ui = Ui_SecondWindow()
        ui.setupUi(self.second_window, excel_dir)
        if self.sender() == self.file1_button:
            self.ui1 = ui
        else:
            self.ui2 = ui
        self.second_window.show()

    def update_slider_labels(self):
        slider_map = {
            self.gaussian_filter_slider: ("Gaussian Smoothening: ", self.gaussian_filter_label, 'sigmaGaussian', 1),
            self.num_of_contours_slider: ("Number of Contours: ", self.num_of_contours_label, 'numOfContour', 1),
            self.color_intensity_slider: ("Color Intensity: ", self.color_intensity_label, 'colorMapIntensity', 100.),
            self.contour_lines_intensity_slider: ("Contour Lines Intensity: ", self.contour_lines_intensity_label, 'colorLinesIntensity', 100.)
        }
        sender = self.sender()
        if sender in slider_map:
            label_text, label_widget, status_key, divisor = slider_map[sender]
            value = sender.value() / divisor
            if status_key == 'numOfContour':
                value = int(value)
            label_widget.setText(f"{label_text}{sender.value()}")
            self.status[status_key] = value
            logging.info(f"Updated {status_key}: {value} (from {label_text})")

    def change_sliders(self):
        
        self.update_slider_labels()
        if not self.plot_ready:
            return
        
        #self.plotter.figure.clear()
        plot_status = self.get_plot_args()
        self.plotter.plot(**plot_status)
        self.canvas.draw()
        logging.info("Updated figure with new slider values.")

    def change_status(self):
        sender = self.sender()
        recalc_required = False
        matched = False  # debugging tool

        recalc_controls = {
            self.gaussian_filter_slider,
            self.node_attenuation_checkbox,
            self.corr_type_group,
            self.pca_reconstruction_components_combobox,
            self.reference_spectra_group
        }

        for control, func in self.get_update_functions().items():
            if isinstance(control, QButtonGroup):
                if sender == control or sender in control.buttons():
                    func()
                    if control in recalc_controls:
                        recalc_required = True
                    matched = True
                    break
            elif sender == control:
                func()
                if control in recalc_controls:
                    recalc_required = True
                matched = True
                break

        if not matched:
            logging.warning(f"[change_status] No update function matched for sender: {repr(sender)}")

        if not self.plot_ready:
            return

        if recalc_required:
            self.recalculate_correlation()

        plot_status = self.get_plot_args()
        #self.figure.clear()
        self.plotter.plot(**plot_status)
        self.canvas.draw()


    def get_update_functions(self):
        return {
            self.node_attenuation_checkbox: self.update_node_att_bool,
            self.corr_type_group: self.update_correlation_type,
            self.pca_reconstruction_components_combobox: self.update_pca_reconstruction_components,
            self.reference_spectra_group: self.update_ref_spectra,
            self.sync_diagonals_group: self.update_sync_diag,
            self.async_diagonals_group: self.update_async_diag,
            self.x_axis_group: self.update_x_axis,
            self.shown_graph_group: self.update_shown_graph,
            self.color_map_box: self.update_color_map,
            self.locator_box: self.update_locator,
            self.contour_lines_color_box: self.update_color_lines,
            self.peaks_signs_group: self.update_signs
        }
    
    def get_plot_args(self):
        plot_keys = {
            'colorMap', 'numOfContour', 'locator_choice', 'syncDiag', 
            'asyncDiag', 'xAxis', 'colorMapIntensity', 'colorLines', 
            'colorLinesIntensity', 'shownGraph', 'peaks_signs'
        }
        return {k: v for k, v in self.status.items() if k in plot_keys}


    def recalculate_correlation(self):
        try:
            calc_method = self.status.get('calcMethod', 'default')
            logging.info(f"Recalculating correlation using method: {calc_method}")
            self.correlation_model.syn(method=self.status['calcMethod'])
            self.correlation_model.asyn(method=self.status['calcMethod'])
            logging.info("Correlation recalculation completed successfully.")
        except Exception as e:
            error_msg = f"An error occurred during recalculation: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "Calculation Error", error_msg)

    def set_status_value(self, key, value):
        self.status[key] = value
        logging.info(f"Updated {key}: {value}")

    def update_node_att_bool(self):
        self.set_status_value('node_attenuation', self.node_attenuation_checkbox.isChecked())

    def update_pca_reconstruction_components(self):
        self.set_status_value('reconstruction_components', int(self.pca_reconstruction_components_combobox.currentText()))

    def update_correlation_type(self):
        self.set_status_value('corrType', 'homo' if self.homo_corr_button.isChecked() else 'hetero')

    def update_calc_method(self):
        self.set_status_value('calcMethod', 'HT' if self.hilbert_transform_button.isChecked() else 'FFT')

    def update_ref_spectra(self):
        ref_map = {
            self.mean_button: 'mean',
            self.initial_button: 'ini',
            self.final_button: 'end'
        }
        self.set_status_value('refSpectra', next((val for btn, val in ref_map.items() if btn.isChecked()), 'zero'))

    def update_sync_diag(self):
        self.set_status_value('syncDiag', 'main' if self.sync_main_diag_button.isChecked() else 'anti')

    def update_async_diag(self):
        self.set_status_value('asyncDiag', 'main' if self.async_main_diag_button.isChecked() else 'anti')

    def update_x_axis(self):
        self.set_status_value('xAxis', 'increasing' if self.increasing_x_button.isChecked() else 'decreasing')

    def update_shown_graph(self):
        graph_map = {
            self.sync_graph_option: 'sync',
            self.async_graph_option: 'async'
        }
        self.set_status_value('shownGraph',
                              next((val for btn, val in graph_map.items() if btn.isChecked()), 'both'))

    def update_signs(self):
        map = {
            self.positive_signs_option: 'positive',
            self.negative_signs_option: 'negative'
        }
        self.set_status_value('peaks_signs',
                              next((val for btn, val in map.items() if btn.isChecked()), 'all'))


    def update_color_map(self):
        self.set_status_value('colorMap', self.color_map_box.currentText())

    def update_locator(self):
        self.set_status_value('locator_choice', self.locator_box.currentText())

    def update_color_lines(self):
        self.set_status_value('colorLines', self.contour_lines_color_box.currentText())

    def plot_button_function(self):
        plot_status = self.get_plot_args()

        try:
            if hasattr(self, 'ui1') and self.format1 == "xlsx":
                location = [self.ui1.sheet, self.ui1.row, self.ui1.column, self.ui1.labeledColumns.isChecked()]
                self.filename1 += location

            if hasattr(self, 'ui2') and self.format2 == "xlsx":
                location = [self.ui2.sheet, self.ui2.row, self.ui2.column, self.ui2.labeledColumns.isChecked()]
                self.filename2 += location

            self.correlation_model = self.controller.build_model(self.filename1, self.filename2, self.status)
            if self.correlation_model:
                self.plotter = CorrelationPlotter(model = self.correlation_model, figure = self.figure, canvas = self.canvas)
                self.plotter.plot(**plot_status)
                self.plot_ready = True
                logging.info("Plot generated succesfully.")

        except ValueError as ve:
            logging.warning(f"Validation Error: {ve}")
            QMessageBox.warning(self, "Validation Error", f"{ve}")
        except Exception as e:
            logging.exception("Unexpected error in plot_button_function")
            QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred: {str(e)}")

    def plot_tridimensional(self):
        # Check if the correlation object exists and appears ready.
        if self.correlation_model is None:
            logging.info("3D plot not generated because the correlation object is not ready.")
            QMessageBox.information(self, "Information", "Please generate the 2D correlation plot first.")
            return
        try:
            # Optionally, you might clear or prepare a separate 3D canvas if needed.
            color_map = self.status.get('colorMap', 'coolwarm')
            self.plotter.plot3d(color_map=color_map)
            logging.info("3D plot generated successfully.")
        except Exception as e:
            logging.exception("Error generating 3D plot.")
            QMessageBox.critical(self, "3D Plot Error", f"An error occurred while generating the 3D plot: {str(e)}")
