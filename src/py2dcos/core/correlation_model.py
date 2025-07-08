from __future__ import annotations

from py2dcos.core.correlation import TwoDCorrelation
from py2dcos.core.io import reader, checkHeader
from py2dcos.plotting.correlation_plot import CorrelationPlotter
from py2dcos.core.preprocessing import PCAProcessor
from py2dcos.core.filters import apply_gaussian_filter, apply_node_attenuation


class CorrelationModel:

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

        if not filename2:
            filename2 = filename1.copy()

        def _normalise(path_or_list):
            if isinstance(path_or_list, str):
                return [path_or_list, path_or_list.split(".")[-2]]
            return path_or_list

        filename1 = _normalise(filename1)
        filename2 = _normalise(filename2)

        spec1 = checkHeader(reader(filename1))
        spec2 = checkHeader(reader(filename2))

        pca = PCAProcessor()
        spec1 = pca.apply(spec1, n_components=reconstruction_comps, report_filename="pca_report1.txt")
        spec2 = pca.apply(spec2, n_components=reconstruction_comps, report_filename="pca_report2.txt")

        if sigma_gaussian > 0:
            spec1 = apply_gaussian_filter(spec1, sigma=sigma_gaussian)
            spec2 = apply_gaussian_filter(spec2, sigma=sigma_gaussian)

        if node_attenuation:
            spec1 = apply_node_attenuation(spec1)
            spec2 = apply_node_attenuation(spec2)

        desc1 = spec1.T.describe().T
        desc2 = spec2.T.describe().T

        ref_map = {
            "zero":  (spec1, spec2),
            "mean":  (spec1.sub(desc1["mean"], axis=0), spec2.sub(desc2["mean"], axis=0)),
            "min":   (spec1.sub(desc1["min"], axis=0),  spec2.sub(desc2["min"], axis=0)),
            "max":   (spec1.sub(desc1["max"], axis=0),  spec2.sub(desc2["max"], axis=0)),
            "ini":   (spec1.sub(spec1[1], axis=0),      spec2.sub(spec2[1], axis=0)),
            "end":   (spec1.sub(spec1.iloc[:, -1], axis=0), spec2.sub(spec2.iloc[:, -1], axis=0)),
        }
        spec1_, spec2_ = ref_map.get(ref, (spec1, spec2))

        self.describe1 = desc1
        self.describe2 = desc2
        self.first1, self.last1 = spec1[1], spec1.iloc[:, -2]
        self.first2, self.last2 = spec2[1], spec2.iloc[:, -2]

        self.core = TwoDCorrelation(spec1_, spec2_)
        self.syncr = self.core.sync(method=method)
        self.asyncr = self.core.async_(method=method)

        # Canvas can be injected later by the GUI
        self.canvas_: None | object = None

    def syn(self, method: str = "HT"):
        self.syncr = self.core.sync(method=method)

    def asyn(self, method: str = "HT"):
        self.asyncr = self.core.async_(method=method)

    """
    def plot(self, *, figure=None, canvas: bool = False, **plot_kwargs):
        plotter = CorrelationPlotter(
            syncr=self.syncr,
            asyncr=self.asyncr,
            describe1=self.describe1,
            describe2=self.describe2,
            first1=self.first1,
            last1=self.last1,
            first2=self.first2,
            last2=self.last2,
            figure=figure,
            canvas=self.canvas_ if canvas else None,
        )
        return plotter.plot(canvas=canvas, **plot_kwargs)

    """