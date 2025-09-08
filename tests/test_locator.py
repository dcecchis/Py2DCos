# tests/test_app_controller.py
# -*- coding: utf-8 -*-
import pytest
import pandas as pd
from pathlib import Path
from PyQt5.QtCore import Qt
from py2dcos.controller.app_controller import AppController
from py2dcos.config.resources import CorrType, ShownGraph, PeaksSigns, CalcMethod
from py2dcos.gui.state.gui_snapshot import GuiSnapshot
from py2dcos.datatypes import InputFile, MathSettings, PlotSettings

# DummyModel and dummy plot functions
class DummyModel: pass

def dummy_plot2d(model, plot, figure=None): return "fig2d"

def dummy_plot3d(model, plot, which): return "fig3d"

@pytest.fixture(autouse=True)
def stub_dependencies(monkeypatch):
    # stub DataLoader.load
    df = pd.DataFrame([[1,2],[3,4]])
    monkeypatch.setattr(
        'py2dcos.controller.app_controller.DataLoader.load',
        lambda f: df.copy()
    )
    # stub CorrelationModel
    monkeypatch.setattr(
        'py2dcos.controller.app_controller.CorrelationModel',
        lambda *args, **kwargs: DummyModel()
    )
    # stub PlotCache.get
    monkeypatch.setattr(
        'py2dcos.controller.app_controller.PlotCache.get',
        lambda self, proj, which: None
    )
    # stub plotting backends
    monkeypatch.setattr(
        'py2dcos.controller.app_controller.plot_sync2d',
        dummy_plot2d
    )
    monkeypatch.setattr(
        'py2dcos.controller.app_controller.plot_async2d',
        dummy_plot2d
    )
    monkeypatch.setattr(
        'py2dcos.controller.app_controller.plot_both2d',
        dummy_plot2d
    )
    monkeypatch.setattr(
        'py2dcos.controller.app_controller.plot3d',
        dummy_plot3d
    )

@pytest.fixture
def controller(qtbot):
    return AppController()

# 1. Missing files errors
@pytest.mark.parametrize("file1,file2,corr_type,expected_msg", [
    (None, None, CorrType.HOMO, "Select at least one input file."),
    (InputFile(path='p1', extension='csv', excel_params=None), None, CorrType.HETERO,
     "Select the second file or switch to homocorrelation.")
])
def test_missing_file_errors(controller, qtbot, file1, file2, corr_type, expected_msg):
    snap = GuiSnapshot(
        file1=file1,
        file2=file2,
        corr_type=corr_type,
        math=MathSettings(),
        plot=PlotSettings(shown_graph=ShownGraph.SYNC, peaks=PeaksSigns.POSITIVE),
        show_3d=False
    )
    msgs = []
    controller.error.connect(lambda m: msgs.append(m))
    controller.update_snapshot(snap, force=True)
    assert msgs == [expected_msg]

# 2. Full rebuild+2D plot
def test_full_cycle_2d(controller):
    f1 = InputFile(path='p1', extension='csv', excel_params=None)
    snap = GuiSnapshot(
        file1=f1, file2=None, corr_type=CorrType.HOMO,
        math=MathSettings(),
        plot=PlotSettings(shown_graph=ShownGraph.SYNC, peaks=PeaksSigns.POSITIVE),
        show_3d=False
    )
    events = []
    controller.busy.connect(lambda: events.append('busy'))
    controller.ready.connect(lambda: events.append('ready'))
    controller.fig2d_ready.connect(lambda fig: events.append(('fig2d', fig)))
    controller.status_text.connect(lambda txt: events.append(('status', txt)))

    controller.update_snapshot(snap, force=True)
    assert events == ['busy', 'ready', ('fig2d','fig2d'), ('status','Ready')]

# 3. Full rebuild+3D plot
def test_full_cycle_3d(controller):
    f1 = InputFile(path='p1', extension='csv', excel_params=None)
    snap = GuiSnapshot(
        file1=f1, file2=None, corr_type=CorrType.HOMO,
        math=MathSettings(),
        plot=PlotSettings(shown_graph=ShownGraph.SYNC, peaks=PeaksSigns.POSITIVE),
        show_3d=True
    )
    events = []
    controller.busy.connect(lambda: events.append('busy'))
    controller.ready.connect(lambda: events.append('ready'))
    controller.fig3d_ready.connect(lambda fig: events.append(('fig3d', fig)))
    controller.status_text.connect(lambda txt: events.append(('status', txt)))
    controller.parent_figure = 'parent'

    controller.update_snapshot(snap, force=True)
    assert events == ['busy', 'ready', ('fig3d','fig3d'), ('status','Ready')]

# 4. math_changed and plot_changed logic
def test_math_and_plot_changed():
    old = GuiSnapshot(file1=None, file2=None, corr_type=CorrType.HOMO,
                      math=MathSettings(method=CalcMethod.HT),
                      plot=PlotSettings(shown_graph=ShownGraph.SYNC, peaks=PeaksSigns.POSITIVE),
                      show_3d=False)
    new = GuiSnapshot(file1=None, file2=None, corr_type=CorrType.HOMO,
                      math=MathSettings(method=CalcMethod.HT, reconstruction_comps=1),
                      plot=old.plot, show_3d=False)
    assert AppController()._math_changed(old, new)
    assert not AppController()._plot_changed(old, new)
    newer = GuiSnapshot(file1=None, file2=None, corr_type=CorrType.HOMO,
                        math=new.math,
                        plot=PlotSettings(shown_graph=ShownGraph.BOTH, peaks=PeaksSigns.POSITIVE),
                        show_3d=True)
    assert not AppController()._math_changed(new, newer)
    assert AppController()._plot_changed(new, newer)
