from py2dcos.core.io import reader
import os

def test_reader_csv_roundtrip(tmp_path):
    import pandas as pd
    data = pd.DataFrame([[1, 2], [3, 4]], index=[1000, 2000])
    temp_file = tmp_path / "test.csv"
    data.to_csv(temp_file, header=False)

    result = reader([str(temp_file), "csv"])
    assert result.shape == data.shape
    assert (result.values == data.values).all()