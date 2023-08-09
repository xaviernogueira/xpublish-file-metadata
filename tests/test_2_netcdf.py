import pytest
import xpublish
import xarray as xr
from fastapi.testclient import TestClient
from pathlib import Path

from xpublish_file_metadata import FileMetadataPlugin

PREFIX = 'datasets/netcdf/file-metadata'

@pytest.fixture(scope='module')
def hide_attrs() -> dict[str, list[str]]:
    """Return a list of attributes to hide."""
    return {
        'netcdf': [
            'platform',
            'description',
        ],
    }

@pytest.fixture(scope='module')
def answers() -> dict[str, str]:
    """Return a dictionary of answers."""
    return {
        'Conventions': 'COARDS',
        'title': '4x daily NMC reanalysis (1948)',
        'references': 'http://www.esrl.noaa.gov/psd/data/gridded/data.ncep.reanalysis.html',
    }

@pytest.fixture(scope='module')
def netcdf_dataset() -> xr.Dataset:
    """Return a xarray dataset with a NetCDF source."""
    air_ds = xr.tutorial.open_dataset('air_temperature')
    assert isinstance(air_ds, xr.Dataset)
    assert isinstance(air_ds.encoding['source'], str)
    assert Path(air_ds.encoding['source']).exists()
    assert air_ds.encoding['source'].endswith('.nc')
    return air_ds

@pytest.fixture(scope='module')
def xpublish_server(
    netcdf_dataset: xr.Dataset,
    hide_attrs: dict[str, list[str]],
) -> xpublish.Rest:
    """Return a TestClient instance with the FileMetadataPlugin."""
    server_obj = xpublish.Rest(
        {'netcdf': netcdf_dataset},
        plugins={'file_metadata': FileMetadataPlugin(hide_attrs=hide_attrs)},
    )
    return server_obj

@pytest.fixture(scope='module')
def client(xpublish_server: TestClient) -> TestClient:
    """Return a TestClient instance with the FileMetadataPlugin."""
    app = xpublish_server.app
    client = TestClient(app)
    return client

def test_full_metadata(client: TestClient) -> None:
    """Test the full metadata endpoint."""
    response = client.get(PREFIX)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert 'format' in response.json().keys()
    assert 'attrs' in response.json().keys()

def test_format(client: TestClient) -> None:
    """Test the format property."""
    response = client.get(f'{PREFIX}/format')
    assert response.status_code == 200
    assert response.json() == 'netcdf'

def test_attrs(
    client: TestClient,
    answers: dict[str, str],
    hide_attrs: dict[str, list[str]],
) -> None:
    """Test the attrs property."""
    response = client.get(f'{PREFIX}/attrs')
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json() == answers
    assert hide_attrs['netcdf'][0] not in response.json().keys()
    assert hide_attrs['netcdf'][1] not in response.json().keys()

def test_attr_names(
    client: TestClient,
    answers: dict[str, str],
    hide_attrs: dict[str, list[str]],
) -> None:
    """Test the attr_names property."""
    response = client.get(f'{PREFIX}/attr-names')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json() == list(answers.keys())
    assert hide_attrs['netcdf'][0] not in response.json()
    assert hide_attrs['netcdf'][1] not in response.json()

def test_single_attr(
    client: TestClient,
    answers: dict[str, str],
) -> None:
    """Test the single_attr property."""
    attr_name = list(answers.keys())[0]
    response = client.get(f'{PREFIX}/attrs/{attr_name}')
    assert response.status_code == 200
    assert isinstance(response.json(), str)
    assert response.json() == answers[attr_name]


