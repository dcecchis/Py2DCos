import pandas as pd
from scipy.ndimage import gaussian_filter
import numpy as np

def apply_gaussian_filter(spec, sigma):
    # accept either a single number for smoothing rows only or a tuple for both axes
    if isinstance(sigma, (int, float)):
        sigma = (sigma, 0)

    # apply gaussian filter to smooth spectral intensities along rows
    smoothed_array = gaussian_filter(spec.values, sigma=sigma)

    # reconstruct dataframe with original wavenumber index and variable columns
    return pd.DataFrame(smoothed_array, index=spec.index, columns=spec.columns)
    
def apply_node_attenuation(spec, a=5, lam=5, eps=1e-7):
    # prepare numeric wavenumber array for derivative calculations
    wavenumbers = spec.index.astype(float).to_numpy()

    # compute average intensity across variables at each wavenumber
    avg_spec = spec.mean(axis=1).to_numpy()

    # approximate first derivative of average spectrum wrt wavenumbers
    A_prime = np.gradient(avg_spec, wavenumbers)
    # approximate second derivative for curvature information
    A_double = np.gradient(A_prime, wavenumbers)

    # build ratio for attenuation calculation, adding eps to avoid zero division
    numerator = (A_double * avg_spec) - eps
    denominator = lam * (A_prime ** 2) + np.abs(A_double * avg_spec) + eps
    ratio = numerator / denominator

    # compute attenuation filter values that suppress noise around nodes
    N_filter = np.exp(-a * (1.0 + ratio))

    # apply the attenuation factor to each row, preserving original data shape
    attenuated_spec = spec.multiply(N_filter, axis=0)
    return attenuated_spec
