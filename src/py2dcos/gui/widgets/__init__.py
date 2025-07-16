# import each widget class so this package exposes them in a single namespace
from .correlation_type_box import CorrelationTypeBox    # choose homo/heterocorrelation
from .input_files_box       import InputFilesBox        # file selection controls
from .data_treatment_box    import DataTreatmentBox     # pca, smoothing, attenuation settings
from .reference_spectra_box import ReferenceSpectraBox  # reference spectrum method selector
from .graph_settings_box    import GraphSettingsBox     # contour, locator, colormap controls
from .diagonals_axes_box    import DiagonalsAxesBox     # sync/async diagonal and axis direction
from .shown_graph_box       import ShownGraphBox        # toggle which graph and peak signs to show

# define the public api: only these classes are imported on `from widgets import *`
__all__ = [
    "CorrelationTypeBox",
    "InputFilesBox",
    "DataTreatmentBox",
    "ReferenceSpectraBox",
    "GraphSettingsBox",
    "DiagonalsAxesBox",
    "ShownGraphBox",
]
