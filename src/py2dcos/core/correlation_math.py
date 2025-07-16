import numpy as np
import pandas as pd

class TwoDCorrelation:
    """
    class to compute synchronous and asynchronous 2d correlation maps

    reads in two spectra dataframes, applies chosen correlation method,
    and returns dataframes of correlation intensities
    """

    def __init__(self, spec1: pd.DataFrame, spec2: pd.DataFrame = None):
        # allow homocorrelation by duplicating first spectrum when second is missing
        if spec2 is None:
            spec2 = spec1.copy()

        # store original spectra for correlation
        self.spec1 = spec1
        self.spec2 = spec2

        # placeholders for computed correlation maps
        self.syncr = None
        self.asyncr = None

        # compute basic statistics once for reference baseline calculations
        self.describe1 = spec1.transpose().describe().transpose()
        self.describe2 = spec2.transpose().describe().transpose()
    
    def noda(self):
        # build weight matrix for hilbert transform (nodal weights)
        nn = len(self.spec1.columns)
        # pattern for hilbert weight values based on lag distances
        fill_pattern = [1.0 / (np.pi * float(i)) if i != 0 else 0.0 for i in range(nn)]
        noda_matrix = np.empty((nn, nn), dtype=float)
        for i in range(nn):
            # negative and positive lag contributions for each row
            left = [-fill_pattern[i - j] for j in range(i)]
            right = [fill_pattern[j] for j in range(nn - i)]
            noda_matrix[i, :] = left + right
        return noda_matrix

    def sync(self, method="HT"):
        # compute synchronous correlation map based on chosen method
        if method == "HT":
            # direct matrix multiplication formula normalised by number of variables
            factor = float(len(self.spec1.columns) - 1)
            self.syncr = pd.DataFrame(
                self.spec1.values @ self.spec2.values.T / factor,
                index=self.spec1.index,
                columns=self.spec2.index
            )
        elif method == "FFT":
            # use fft to transform and correlate in frequency domain
            scale = (float(self.spec1.shape[1])) ** 0.5
            xfft = np.fft.fft(self.spec1.values, axis=1) / scale
            yfft = np.fft.fft(self.spec2.values, axis=0) / scale
            X = xfft @ np.conj(yfft).T / float(self.spec1.shape[0])
            # keep only real part for synchronous correlation
            self.syncr = pd.DataFrame(
                np.real(X),
                index=self.spec1.index,
                columns=self.spec2.index
            )
        return self.syncr

    def async_(self, method="HT"):
        # compute asynchronous correlation map based on chosen method
        if method == "HT":
            # apply hilbert-based nodal weights between spectra
            factor = float(len(self.spec1.columns) - 1)
            self.asyncr = pd.DataFrame(
                self.spec1.values @ self.noda() @ self.spec2.values.T / factor,
                index=self.spec1.index,
                columns=self.spec2.index
            )
        elif method == "FFT":
            # use fft to obtain imaginary part for asynchronous correlation
            scale = (float(self.spec1.shape[1])) ** 0.5
            xfft = np.fft.fft(self.spec1.values, axis=1) / scale
            yfft = np.fft.fft(self.spec2.values, axis=1) / scale
            X = xfft @ np.conj(yfft).T / (self.spec1.shape[0] - 1)
            self.asyncr = pd.DataFrame(
                np.imag(X),
                index=self.spec1.index,
                columns=self.spec2.index
            )
        return self.asyncr
