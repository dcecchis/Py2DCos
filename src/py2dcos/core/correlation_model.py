from __future__ import annotations

from py2dcos.core.correlation_math import TwoDCorrelation
from py2dcos.core.io import reader, checkHeader
from py2dcos.core.pca_preprocessing import PCAProcessor
from py2dcos.core.filters import apply_gaussian_filter, apply_node_attenuation

class CorrelationModel:
    """
    encapsulates the data flow for computing 2d correlations

    reads input files, applies preprocessing (pca, smoothing, attenuation),
    applies baseline reference, and computes sync and async maps
    """

    def __init__(
        self,
        filename1,
        filename2: str | list = "",
        *,
        ref: str = "ini",
        method: str = "HT",
        reconstruction_comps: int = 0,
        sigma_gaussian: float = 0.0,
        node_attenuation: bool = False,
    ):
        # allow using a single file for homocorrelation by duplicating filename1
        if not filename2:
            filename2 = filename1

        def _normalise(path_or_list):
            # ensure filename parameters are in [path, ext] format for reader
            if isinstance(path_or_list, str):
                # extract extension segment before dot
                return [path_or_list, path_or_list.split(".")[-2]]
            return path_or_list

        filename1 = _normalise(filename1)
        filename2 = _normalise(filename2)

        # read dataframes and fix headers to uniform numeric indices
        spec1 = checkHeader(reader(filename1))
        spec2 = checkHeader(reader(filename2))

        # apply pca reconstruction if components requested to reduce noise
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
        ref_map = {
            "zero":  (spec1, spec2),
            "mean":  (spec1.sub(desc1["mean"], axis=0), spec2.sub(desc2["mean"], axis=0)),
            "min":   (spec1.sub(desc1["min"], axis=0),  spec2.sub(desc2["min"], axis=0)),
            "max":   (spec1.sub(desc1["max"], axis=0),  spec2.sub(desc2["max"], axis=0)),
            "ini":   (spec1.sub(spec1[1], axis=0),      spec2.sub(spec2[1], axis=0)),
            "end":   (spec1.sub(spec1.iloc[:, -1], axis=0), spec2.sub(spec2.iloc[:, -1], axis=0)),
        }
        # pick the pair of spectra after baseline subtraction
        spec1_, spec2_ = ref_map.get(ref, (spec1, spec2))

        # store stats and boundary spectra for potential external use
        self.describe1 = desc1
        self.describe2 = desc2
        self.first1, self.last1 = spec1[1], spec1.iloc[:, -2]
        self.first2, self.last2 = spec2[1], spec2.iloc[:, -2]

        # create and run the core 2d correlation calculations
        self.core = TwoDCorrelation(spec1_, spec2_)
        self.syncr = self.core.sync(method=method)
        self.asyncr = self.core.async_(method=method)

        # placeholder for injecting into a gui canvas if needed later
        self.canvas_: None | object = None

    def syn(self, method: str = "HT"):
        # recompute synchronous correlation with possibly new method
        self.syncr = self.core.sync(method=method)

    def asyn(self, method: str = "HT"):
        # recompute asynchronous correlation with possibly new method
        self.asyncr = self.core.async_(method=method)

    def is_positive(self) -> bool:
        # return true only if all correlation values across both maps are positive
        return (self.syncr.values > 0).all() and (self.asyncr.values > 0).all()
