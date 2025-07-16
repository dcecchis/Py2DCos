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
    # controller to build and cache correlation model based on user inputs
    def __init__(self):
        # store last input fingerprint to skip redundant model rebuilds
        self._prev_fingerprint: Optional[tuple] = None
        # cache of the most recent correlation model
        self._corr_obj: Optional[CorrelationModel] = None

    # helpers
    @staticmethod
    def _fingerprint(file1, file2, state: GuiState) -> tuple:
        """
        create a hashable snapshot of the current inputs
        """
        def _as_tuple(f):
            # handle file info given either as [path, ext, ...] or plain string
            return tuple(f) if isinstance(f, list) else (f,)

        # include preprocessing parameters in fingerprint to detect any change
        return (
            *_as_tuple(file1),
            *_as_tuple(file2),
            state.sigma_gaussian,
            state.node_attenuation,
            state.calc_method,
            state.ref_spectra,
            state.reconstruction_components,
        )

     # public api
    def build_model(
        self,
        file1,
        file2: Optional[list | str] = None,
        state: GuiState | None = None,
    ) -> CorrelationModel:
        """
        return a ready-to-plot correlation model
        """
        # require gui state to know user settings for preprocessing
        if state is None:
            raise ValueError("`state` (GuiState) must be provided")

        # if second file missing, use first for homocorrelation
        if not file2:
            file2 = file1

        # validate file extensions and chosen correlation method early
        try:
            validate_extension(file1[1], file2[1])
            validate_method(state.calc_method.value)
        except (UnsupportedExtensionError, UnsupportedMethodError) as exc:
            logging.error(str(exc))
            # propagate to ui layer for user notification
            raise

        # detect if inputs or settings changed since last model build
        fp = self._fingerprint(file1, file2, state)
        if fp != self._prev_fingerprint:
            logging.info("creating new correlation model.")
            # build new model with current parameters
            self._corr_obj = CorrelationModel(
                file1,
                file2,
                ref=state.ref_spectra.value,
                method=state.calc_method.value,
                reconstruction_comps=state.reconstruction_components,
                sigma_gaussian=state.sigma_gaussian,
                node_attenuation=state.node_attenuation,
            )
            # update cache key
            self._prev_fingerprint = fp

        # always recompute maps to account for method changes
        logging.info("calculating synchronous correlation.")
        self._corr_obj.syn(method=state.calc_method.value)
        logging.info("calculating asynchronous correlation.")
        self._corr_obj.asyn(method=state.calc_method.value)

        return self._corr_obj

    def data_is_positive(self) -> bool:
        # return true only if model exists and all correlation values are positive
        return bool(self._corr_obj) and self._corr_obj.is_positive()
