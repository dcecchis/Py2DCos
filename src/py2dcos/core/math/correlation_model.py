from __future__ import annotations
import pandas as pd
from py2dcos.config.resources import RefSpectra
from py2dcos.core.math.correlation_math import TwoDCorrelation
from py2dcos.core.math.pca_preprocessing import PCAProcessor
from py2dcos.core.math.filters import apply_gaussian_filter, apply_node_attenuation

class CorrelationModel:
    """
    Accepts two pandas.DataFrame objects (rows = spectra, columns = wavenumbers),
    applies optional preprocessing (PCA, Gaussian smoothing, node attenuation),
    baseline-corrects with the chosen reference, and computes synchronous /
    asynchronous 2-D correlation.
    """

    def __init__(
        self,
        spec1,
        spec2,
        *,
        ref: str = "ini",
        method: str = "HT",
        reconstruction_comps: int = 0,
        sigma_gaussian: float = 0.0,
        node_attenuation: bool = False,
    ):
        if spec1.shape != spec2.shape:
            raise ValueError("spec1 and spec2 must have identical dimensions.")

         # avoid mutating caller’s DataFrames in-place
        spec1, spec2 = spec1.copy(), spec2.copy()
        # apply pca reconstruction if components requested to reduce noise
        if reconstruction_comps > 0:
            pca = PCAProcessor()
            spec1 = pca.apply(spec1, n_components=reconstruction_comps, report_filename="pca_report1.txt")
            spec2 = pca.apply(spec2, n_components=reconstruction_comps, report_filename="pca_report2.txt")

        # smooth spectra with gaussian kernel when sigma positive
        if sigma_gaussian > 0:
            spec1 = apply_gaussian_filter(spec1, sigma=sigma_gaussian)
            spec2 = apply_gaussian_filter(spec2, sigma=sigma_gaussian)

        # apply node attenuation filter to emphasize meaningful features
        if node_attenuation:
            spec1 = apply_node_attenuation(spec1)
            spec2 = apply_node_attenuation(spec2)

        # compute descriptive statistics for each spectrum (transposed then back)
        desc1 = spec1.T.describe().T
        desc2 = spec2.T.describe().T
        
        # define how to subtract reference baseline based on ref key
        ref_map: dict [RefSpectra, tuple[pd.DataFrame, pd.DataFrame]] = {
            RefSpectra.ZERO:  (spec1, spec2),
            RefSpectra.MEAN:  (spec1.sub(desc1["mean"], axis=0), spec2.sub(desc2["mean"], axis=0)),
            RefSpectra.MIN:   (spec1.sub(desc1["min"], axis=0),  spec2.sub(desc2["min"], axis=0)),
            RefSpectra.MAX:   (spec1.sub(desc1["max"], axis=0),  spec2.sub(desc2["max"], axis=0)),
            RefSpectra.INITIAL:   (spec1.sub(spec1[1], axis=0),      spec2.sub(spec2[1], axis=0)),
            RefSpectra.FINAL:   (spec1.sub(spec1.iloc[:, -1], axis=0), spec2.sub(spec2.iloc[:, -1], axis=0)),
        }
        # pick the pair of spectra after baseline subtraction
        spec1_, spec2_ = ref_map[ref]

        # store stats and boundary spectra for potential external use
        self.describe1 = desc1
        self.describe2 = desc2
        self.first1, self.last1 = spec1.iloc[:, 1], spec1.iloc[:, -1]
        self.first2, self.last2 = spec2.iloc[:, 1], spec2.iloc[:, -1]

        # create and run the core 2d correlation calculations
        self.core = TwoDCorrelation(spec1_, spec2_)
        self.syncr = self.core.sync(method=method)
        self.asyncr = self.core.async_(method=method)

        # placeholder for injecting into a gui canvas if needed later
        self.canvas_: None | object = None