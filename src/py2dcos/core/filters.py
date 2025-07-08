import pandas as pd
from scipy.ndimage import gaussian_filter
import numpy as np

def apply_gaussian_filter(spec, sigma):

    if isinstance(sigma, (int, float)):
        sigma = (sigma, 0)

    # Apply Gaussian filter
    smoothed_array = gaussian_filter(spec.values, sigma=sigma)

    # Reconstruct the DataFrame with the same index and columns as the input
    return pd.DataFrame(smoothed_array, index=spec.index, columns=spec.columns)
    
def apply_node_attenuation(spec, a=5, lam=5, eps=1e-7):
    wavenumbers = spec.index.astype(float).to_numpy()

    # Compute the average spectrum over all columns.
    avg_spec = spec.mean(axis=1).to_numpy()

    # Compute first and second derivatives with respect to wavenumbers.
    A_prime = np.gradient(avg_spec, wavenumbers)
    A_double = np.gradient(A_prime, wavenumbers)

    numerator = (A_double * avg_spec) - eps
    denominator =  lam * (A_prime ** 2) + np.abs(A_double * avg_spec) + eps
    ratio = numerator/denominator


    # Compute the node attenuation filter.
    N_filter = np.exp(
        -a * (1.0 + ratio)
    )

    # Apply the filter along the spectral (row) axis and return the new DataFrame.
    attenuated_spec = spec.multiply(N_filter, axis=0)
    return attenuated_spec