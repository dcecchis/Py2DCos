from py2dcos.core.correlation import TwoDCorrelation
from py2dcos.core.io import reader, checkHeader
from py2dcos.core.twoDspeciesNEW import twoDspecies
from py2dcos.core.preprocessing import PCAProcessor
from py2dcos.core.filters import apply_gaussian_filter
from py2dcos.core.filters import apply_node_attenuation

class Legacy2DWrapper:
    def __init__(self, filename1, filename2="", ref='ini', method="HT",
                 reconstruction_comps=0, sigma_gaussian=0, node_attenuation=False):
        # Preprocess input
        if filename2 == "":
            filename2 = filename1
        if isinstance(filename1, str):
            filename1 = [filename1, filename1.split('.')[-2]]
        if isinstance(filename2, str):
            filename2 = [filename2, filename2.split('.')[-2]]

        # Read and sanitize
        spec1 = reader(filename1)
        spec1 = checkHeader(spec1)
        spec2 = reader(filename2)
        spec2 = checkHeader(spec2)

        # PCA preprocessing
        pca_proc = PCAProcessor()
        spec1 = pca_proc.apply(spec1, n_components=reconstruction_comps, report_filename="pca_report1.txt")
        spec2 = pca_proc.apply(spec2, n_components=reconstruction_comps, report_filename="pca_report2.txt")

        # Gaussian smoothing
        if sigma_gaussian > 0:
            spec1 = apply_gaussian_filter(spec1, sigma=sigma_gaussian)
            spec2 = apply_gaussian_filter(spec2, sigma=sigma_gaussian)

        # Node Attenuation
        if node_attenuation:
            spec1 = apply_node_attenuation(spec1)
            spec2 = apply_node_attenuation(spec2)

        describe1 = spec1.transpose().describe().transpose()
        describe2 = spec2.transpose().describe().transpose()

        self.first1 = spec1[1]
        self.first2 = spec2[1]
        self.last1 = spec1[spec1.columns[-2]]
        self.last2 = spec2[spec2.columns[-2]]


        if ref == 'zero':
            spec1_, spec2_ = spec1, spec2
        elif ref == 'mean':
            spec1_ = spec1.sub(describe1['mean'], axis=0)
            spec2_ = spec2.sub(describe2['mean'], axis=0)
        elif ref == 'min':
            spec1_ = spec1.sub(describe1['min'], axis=0)
            spec2_ = spec2.sub(describe2['min'], axis=0)
        elif ref == 'max':
            spec1_ = spec1.sub(describe1['max'], axis=0)
            spec2_ = spec2.sub(describe2['max'], axis=0)
        elif ref == 'ini':
            spec1_ = spec1.sub(spec1[1], axis=0)
            spec2_ = spec2.sub(spec2[1], axis=0)
        elif ref == 'end':
            spec1_ = spec1.sub(spec1[spec1.columns[-1]], axis=0)
            spec2_ = spec2.sub(spec2[spec2.columns[-1]], axis=0)

        self.describe1 = describe1
        self.describe2 = describe2

        # Core math object
        self.core = TwoDCorrelation(
                spec1_,
                spec2_
            )

    def syn(self, method="HT"):
        self.syncr = self.core.sync(method=method)

    def asyn(self, method="HT"):
        self.asyncr = self.core.async_(method=method)

    def plotFunction(self, *args, **kwargs):
        """
        Temporary shim so the GUI can still call .plotFunction().
        spin up a throw-away twoDspecies instance that contains ONLY the
        plotting routines and fake its internal fields so it plots the data
        we already computed.
        """
        temp = twoDspecies.__new__(twoDspecies)          # create naked instance
        # wire in data structures the old plotFunction expects
        temp.syncr = self.syncr
        temp.asyncr = self.asyncr
        temp.describe1 = self.describe1
        temp.describe2 = self.describe2
        temp.first1 = self.first1
        temp.first2 = self.first2
        temp.last1  = self.last1
        temp.last2  = self.last2
        # give it access to the same matplotlib figure / canvas if provided
        temp.canvas_ = getattr(self, "canvas_", None)
        temp.figure  = getattr(self, "figure",  None)
        # finally, forward the plotting call
        return twoDspecies.plotFunction(temp, *args, **kwargs)
