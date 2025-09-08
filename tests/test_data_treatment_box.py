# File: tests/test_data_treatment_box.py
import pytest
from py2dcos.gui.widgets.data_treatment_box import DataTreatmentBox
from py2dcos.gui.state.gui_snapshot import GuiSnapshot
from py2dcos.datatypes import MathSettings

@pytest.fixture
def data_box(qtbot):
    """Create and expose a DataTreatmentBox for testing."""
    snap = GuiSnapshot()
    box = DataTreatmentBox(snap)
    qtbot.addWidget(box)
    box.show()
    qtbot.waitExposed(box)
    return box


def test_update_from_snapshot_syncs_controls(data_box):
    old_math = data_box.snapshot.math
    # create a new MathSettings via update() to preserve other fields
    new_math = old_math.update(
        reconstruction_comps=3,
        sigma_gaussian=5.0,
        node_attenuation=True,
    )
    # update snapshot and apply to widget
    snap2 = data_box.snapshot.update(math=new_math)
    data_box.update_from_snapshot(snap2)

    assert data_box.pca_combo.currentText() == '3'
    assert data_box.gaussian_slider.value() == 5
    # _apply_snapshot uses m.sigma_gaussian for label
    assert data_box.gaussian_label.text() == 'Gaussian smoothing: 5.0'
    assert data_box.node_checkbox.isChecked()


def test_update_gauss_label_changes_text(data_box, qtbot):
    # directly update label
    data_box._update_gauss_label(7)
    assert data_box.gaussian_label.text() == 'Gaussian smoothing: 7'

    # slider valueChanged updates label to its maximum
    max_val = data_box.gaussian_slider.maximum()
    data_box.gaussian_slider.setValue(max_val)
    qtbot.waitUntil(
        lambda: data_box.gaussian_label.text() == f'Gaussian smoothing: {max_val}',
        timeout=500
    )
    assert data_box.gaussian_label.text() == f'Gaussian smoothing: {max_val}'


def test_emit_math_signals_update(data_box, qtbot):
    # PCA combo emits correct math
    with qtbot.waitSignal(data_box.state_changed, timeout=500) as catcher:
        data_box.pca_combo.setCurrentText('2')
        data_box.pca_combo.activated[str].emit('2')
    payload = catcher.args[0]
    assert 'math' in payload
    assert isinstance(payload['math'], MathSettings)
    assert payload['math'].reconstruction_comps == 2

    # Gaussian slider emits correct sigma
    with qtbot.waitSignal(data_box.state_changed, timeout=500) as catcher2:
        data_box.gaussian_slider.setValue(4)
        data_box.gaussian_slider.sliderReleased.emit()
    payload2 = catcher2.args[0]
    assert payload2['math'].sigma_gaussian == 4.0

    # Node attenuation checkbox emits correct boolean
    with qtbot.waitSignal(data_box.state_changed, timeout=500) as catcher3:
        data_box.node_checkbox.click()
    payload3 = catcher3.args[0]
    assert payload3['math'].node_attenuation == data_box.node_checkbox.isChecked()
