import pytest
import xpublish

import xpublish_file_metadata

#@pytest.fixture(scope='module')
def test_formats() -> list[str]:
    """Return a list of optional dependencies that are installed."""
    test_formats = []
    try:
        import netCDF4
        test_formats.append('netcdf')
    except ImportError:
        pass
    try:
        import cfgrib
        test_formats.append('grib')
    except ImportError:
        pass
    except RuntimeError:
        pass
    try:
        import rasterio
        test_formats.append('geotiff')
    except ImportError:
        pass
    try:
        import h5py
        test_formats.append('hdf5')
    except ImportError:
        pass

    return test_formats


def test_namespace() -> None:
    assert 'FileMetadataPlugin' in dir(xpublish_file_metadata)

def test_load_in(test_formats: list[str]) -> None:
    """Tests that all format plugins with dependencies present are loaded in."""
    loaded_formats = xpublish_file_metadata.plugin.load_file_formats()
    for format in test_formats:
        assert format in loaded_formats.keys()
        assert isinstance(loaded_formats[format], xpublish_file_metadata.plugin.FormatProtocol)
    

def test_plugin() -> None:
    assert 'FileMetadataPlugin' in dir(xpublish_file_metadata.plugin)

if __name__ == '__main__':
    test_namespace()
    test_load_in(test_formats())
    test_plugin()
    print('All tests passed!')