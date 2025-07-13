import logging
from typing import Optional

from py2dcos.core.validators import (
    validate_method,
    validate_extension,
    UnsupportedExtensionError,
    UnsupportedMethodError,
)
from py2dcos.core.correlation_model import CorrelationModel
from py2dcos.gui.state import GuiState


class AppController:

    def __init__(self):
        self._prev_fingerprint: Optional[tuple] = None
        self._corr_obj: Optional[CorrelationModel] = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _fingerprint(file1, file2, state: GuiState) -> tuple:
        """
        Create a hashable snapshot of the inputs
        """
        def _as_tuple(f):
            # file info arrives as [filepath, ext, …] or a str path
            return tuple(f) if isinstance(f, list) else (f,)

        return (
            *_as_tuple(file1),
            *_as_tuple(file2),
            state.sigma_gaussian,
            state.node_attenuation,
            state.calc_method,
            state.ref_spectra,
            state.reconstruction_components,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def build_model(
        self,
        file1,
        file2: Optional[list | str] = None,
        state: GuiState | None = None,
    ) -> CorrelationModel:
        """
        Return a ready-to-plot CorrelationModel.
        """
        if state is None:
            raise ValueError("`state` (GuiState) must be provided")

        # Homocorrelation shortcut
        if not file2:
            file2 = file1

        # Validation
        try:
            # file1[1] and file2[1] are the extensions
            validate_extension(file1[1], file2[1])
            validate_method(state.calc_method.value)  # Enum → str
        except (UnsupportedExtensionError, UnsupportedMethodError) as exc:
            logging.error(str(exc))
            raise  # GUI catches and shows message box


        # Detect changes (to avoid redundant work)
        fp = self._fingerprint(file1, file2, state)

        if fp != self._prev_fingerprint:
            logging.info("Creating new CorrelationModel.")
            self._corr_obj = CorrelationModel(
                file1,
                file2,
                ref=state.ref_spectra.value,
                method=state.calc_method.value,
                reconstruction_comps=state.reconstruction_components,
                sigma_gaussian=state.sigma_gaussian,
                node_attenuation=state.node_attenuation,
            )
            self._prev_fingerprint = fp

        # Calculate / update correlations
        logging.info("Calculating synchronous correlation.")
        self._corr_obj.syn(method=state.calc_method.value)

        logging.info("Calculating asynchronous correlation.")
        self._corr_obj.asyn(method=state.calc_method.value)

        return self._corr_obj

    def data_is_positive(self) -> bool:
        return bool(self._corr_obj) and self._corr_obj.is_positive()
