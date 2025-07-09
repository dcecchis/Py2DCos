import pandas as pd
from scipy.ndimage import gaussian_filter
import numpy as np

def apply_gaussian_filter(spec, sigma):
    # allow scalar sigma for row-only smoothing
    if isinstance(sigma, (int, float)):
        sigma = (sigma, 0)

    # smooth values with Gaussian kernel
    smoothed_array = gaussian_filter(spec.values, sigma=sigma)

    # rebuild DataFrame with original labels
    return pd.DataFrame(smoothed_array, index=spec.index, columns=spec.columns)
    
def apply_node_attenuation(spec, a=5, lam=5, eps=1e-7):
    # convert index to numeric wavenumbers
    wavenumbers = spec.index.astype(float).to_numpy()

    # average across columns for attenuation calculation
    avg_spec = spec.mean(axis=1).to_numpy()

    # first and second derivatives wrt wavenumbers
    A_prime = np.gradient(avg_spec, wavenumbers)
    A_double = np.gradient(A_prime, wavenumbers)

    # compute ratio used in attenuation exponent
    numerator = (A_double * avg_spec) - eps
    denominator =  lam * (A_prime ** 2) + np.abs(A_double * avg_spec) + eps
    ratio = numerator/denominator


    # node attenuation filter values per row
    N_filter = np.exp(
        -a * (1.0 + ratio)
    )

    # scale each row by its attenuation factor
    attenuated_spec = spec.multiply(N_filter, axis=0)
    return attenuated_spec