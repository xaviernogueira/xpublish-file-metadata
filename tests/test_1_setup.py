import pytest
import xpublish
import xarray as xr

import xpublish_file_metadata

@pytest.fixture(scope='module')
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


@pytest.fixture(scope='module')
def test_server() -> xpublish.Rest:
    """Return a TestClient instance with the FileMetadataPlugin."""
    server_obj = xpublish.Rest(
        {'test': xr.tutorial.open_dataset('air_temperature')},
        plugins={'file-metadata': xpublish_file_metadata.FileMetadataPlugin()},
    )
    assert isinstance(server_obj, xpublish.Rest)
    return server_obj


def test_plugin() -> None:
    assert 'FileMetadataPlugin' in dir(xpublish_file_metadata)
    
    plugin = xpublish_file_metadata.FileMetadataPlugin()
    assert plugin.name == 'file-metadata'
    assert plugin.dataset_router_prefix == '/file-metadata'
    assert plugin.dataset_router_tags == ['file-metadata']
    assert isinstance(plugin.loaded_formats, dict)
    assert isinstance(plugin.hide_attrs, dict)


def test_load_in(test_formats: list[str]) -> None:
    """Tests that all format plugins with dependencies present are loaded in."""
    loaded_formats = xpublish_file_metadata.plugin.load_file_formats()
    for format in test_formats:
        assert format in loaded_formats.keys()
        assert isinstance(loaded_formats[format], xpublish_file_metadata.plugin.FormatProtocol)
    

def test_xpublish_compatibility(test_server: xpublish.Rest) -> None:
    """Tests that the plugin can be loaded into xpublish."""
    assert 'file-metadata' in test_server.plugins.keys()
    assert isinstance(
        test_server.plugins['file-metadata'],
        xpublish_file_metadata.FileMetadataPlugin,
    )

def test_plugin_routes(test_server: xpublish.Rest) -> None:
    route_names = [route.name for route in test_server.app.routes]
    assert 'supported_formats' in route_names
    assert 'file_format' in route_names
    assert 'metadata' in route_names
    assert 'attrs' in route_names
    assert 'attr_names' in route_names
    assert 'single_attr' in route_names
