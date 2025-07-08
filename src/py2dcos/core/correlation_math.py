import numpy as np
import pandas as pd

class TwoDCorrelation:
    def __init__(self, spec1: pd.DataFrame, spec2: pd.DataFrame = None):
        if spec2 is None:
            spec2 = spec1.copy()

        self.spec1 = spec1
        self.spec2 = spec2

        self.syncr = None
        self.asyncr = None

        self.describe1 = spec1.transpose().describe().transpose()
        self.describe2 = spec2.transpose().describe().transpose()
    
    def noda(self):
        nn = len(self.spec1.columns)
        fill_pattern = [1. / (np.pi * float(i)) if i != 0 else 0. for i in range(nn)]
        noda_matrix = np.empty((nn, nn), dtype=float)
        for i in range(nn):
            noda_matrix[i, :] = [-fill_pattern[i - j] for j in range(i)] + [fill_pattern[j] for j in range(nn - i)]
        return noda_matrix

    def sync(self, method="HT"):
        if method == "HT":
            self.syncr = pd.DataFrame(self.spec1.values @ self.spec2.values.T / float(len(self.spec1.columns) - 1),
                                      index=self.spec1.index,
                                      columns=self.spec2.index)
        elif method == "FFT":
            xfft = np.fft.fft(self.spec1.values, axis=1) / (float(self.spec1.shape[1])) ** 0.5
            yfft = np.fft.fft(self.spec2.values, axis=0) / (float(self.spec2.shape[0])) ** 0.5
            X = xfft @ np.conj(yfft).T / float(self.spec1.shape[0])
            self.syncr = pd.DataFrame(np.real(X),
                                      index=self.spec1.index,
                                      columns=self.spec2.index)
        return self.syncr

    def async_(self, method="HT"):
        if method == "HT":
            self.asyncr = pd.DataFrame(
                self.spec1.values @ self.noda() @ self.spec2.values.T / (len(self.spec1.columns) - 1),
                index=self.spec1.index,
                columns=self.spec2.index)
        elif method == "FFT":
            xfft = np.fft.fft(self.spec1.values, axis=1) / (float(self.spec1.shape[1])) ** 0.5
            yfft = np.fft.fft(self.spec2.values, axis=1) / (float(self.spec2.shape[1])) ** 0.5
            X = xfft @ np.conj(yfft).T / (self.spec1.shape[0] - 1)
            self.asyncr = pd.DataFrame(np.imag(X),
                                       index=self.spec1.index,
                                       columns=self.spec2.index)
        return self.asyncr
