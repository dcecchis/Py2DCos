import numpy as np
import pandas as pd
import pytest

from py2dcos.core.io.io import reader, checkHeader, checklabels, interp


# reader: file → DataFrame round-trip
@pytest.mark.parametrize("ext, sep", [("csv", ","), ("txt", " ")])
def test_reader_loads_numeric_matrix(tmp_path, ext, sep):
    # create a small numeric spectrum file
    rng = np.random.default_rng(0)
    df_orig = pd.DataFrame(rng.normal(size=(4, 3)),
                           index=[4000, 3900, 3800, 3700])
    p = tmp_path / f"spec.{ext}"
    df_orig.to_csv(p, header=False, sep=sep)

    # read it back in
    df_read = reader((p, ext))

    # normalise index and labels to compare raw values
    for df in (df_orig, df_read):
        df.index = df.index.astype(float)
        df.index.name = None
        df.columns = range(df.shape[1])    # ignore library’s relabel offset

    # values should match exactly
    pd.testing.assert_frame_equal(df_read, df_orig, atol=1e-12)
