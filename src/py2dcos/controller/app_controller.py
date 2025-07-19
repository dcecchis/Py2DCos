from __future__ import annotations
import logging
import traceback
from typing import Optional
from PyQt5.QtCore import QObject, pyqtSignal
from matplotlib.figure import Figure
from py2dcos.controller.plot_cache import PlotCache
from py2dcos.core.validators import validate_method, validate_extension
from py2dcos.core.math.correlation_model import CorrelationModel
from py2dcos.core.io.loader import DataLoader         
from py2dcos.plotting.backends.plotly_backend import plot3d
from py2dcos.plotting.backends.plot_sync import plot_sync2d
from py2dcos.plotting.backends.plot_async import plot_async2d
from py2dcos.plotting.backends.plot_both import plot_both2d
from py2dcos.gui.state.gui_snapshot import GuiSnapshot
from py2dcos.config.resources import CorrType, ShownGraph
from py2dcos.types import InputFile, MathSettings

logger = logging.getLogger(__name__)

class AppController(QObject):
    # controller to build and cache correlation model based on user inputs

    fig2d_ready = pyqtSignal(object)        # matplotlib Figure
    fig3d_ready = pyqtSignal(object)        # plotly Figure
    error       = pyqtSignal(str)
    status_text = pyqtSignal(str)
    busy  = pyqtSignal() 
    ready = pyqtSignal()   


    def __init__(self):
        super().__init__()
        self.parent_figure: Optional[Figure] = None
        self._plot_cache = PlotCache()
        self._snap_prev: Optional[GuiSnapshot] = None
        self._model:      Optional[CorrelationModel] = None
        self._fig2d:      Optional[object] = None
        self._fig3d:      Optional[object] = None
        self._math_dirty: bool = False 
        
    def update_snapshot(self, snapshot: GuiSnapshot, force: bool = False) -> None:
        try:
            if not snapshot.file1:  # no file uploaded
                if force:  # user pressed plot
                    self.error.emit("Select at least one input file.")
                return

            if snapshot.corr_type is CorrType.HETERO and not snapshot.file2:
                if force:  # plot button pressed and no second file
                    self.error.emit("Select the second file or switch to homocorrelation.")
                return

            math_changed  = self._math_changed(self._snap_prev, snapshot)
            plot_changed  = self._plot_changed(self._snap_prev, snapshot)

            if force:
                self._validate_inputs(snapshot.file1, snapshot.file2 or snapshot.file1, snapshot.math)

                if self._model is None or math_changed or self._math_dirty:
                    self._rebuild_model(snapshot)      # expensive maths
                    self._plot_cache.clear()            # drop old figures
                    self._math_dirty = False 

                # always redraw after Plot is pressed
                self._rebuild_plot(snapshot)
                self.status_text.emit("Ready")
                self._snap_prev = snapshot             # safe to overwrite now
                return   

            # no new maths
            else:
                # user tweaked colours, 3-D toggle, etc.
                if plot_changed and self._model is not None:
                    self._rebuild_plot(snapshot)

                # if math settings changed but Plot not pressed, just notify
                if math_changed:
                    self._math_dirty = True
                    self.status_text.emit("Parameters changed, press Plot")

                if not self._math_dirty:
                    self._snap_prev = snapshot


        except Exception as exc:
            logger.exception("Controller error")
            self.error.emit(str(exc))

    def _math_changed(self, old: GuiSnapshot | None, new: GuiSnapshot) -> bool:
        # this function checks if math parameters changed
        if old is None:
            return True
        return (
            old.file1 != new.file1
            or old.file2 != new.file2
            or old.corr_type != new.corr_type
            or old.math != new.math
        )
    
    def _plot_changed(self, old: GuiSnapshot | None, new: GuiSnapshot) -> bool:
        # this function checks if plotting parameteres changed
        if old is None:
            return True
        return (
            old.plot != new.plot
            or old.show_3d != new.show_3d
        )
    
    # Validation
    @staticmethod
    def _validate_inputs(f1: InputFile, f2: InputFile, math: MathSettings):
        validate_extension(f1.extension, f2.extension)
        validate_method(math.method)

    def _rebuild_model(self, snapshot: GuiSnapshot):
        self.busy.emit()
        f1, f2 = snapshot.file1, snapshot.file2 or snapshot.file1
        spec1 = DataLoader.load(f1)
        spec2 = DataLoader.load(f2)
        self._model = CorrelationModel(
            spec1,
            spec2,
            ref = snapshot.math.ref,
            method = snapshot.math.method,
            reconstruction_comps=snapshot.math.reconstruction_comps,
            sigma_gaussian=snapshot.math.sigma_gaussian,
            node_attenuation=snapshot.math.node_attenuation
        )
        self._plot_cache.clear()
        self.ready.emit()

    def _rebuild_plot(self, snapshot: GuiSnapshot):
        logger.info("Plotting")
        projection = snapshot.show_3d
        which = snapshot.plot.shown_graph
        fig = self._plot_cache.get(projection, which)
        if fig is None:
            if projection:
                self._fig3d = plot3d(self._model, snapshot.plot, which)
                self.fig3d_ready.emit(self._fig3d)
            else:
                fn_2d = {ShownGraph.SYNC: plot_sync2d, ShownGraph.ASYNC: plot_async2d, ShownGraph.BOTH: plot_both2d}[which]
                fig = fn_2d(self._model, snapshot.plot, figure=self.parent_figure)
                self.fig2d_ready.emit(fig) 

