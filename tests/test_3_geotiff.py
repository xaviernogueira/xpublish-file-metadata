import pytest
import xpublish
import rioxarray
import xarray as xr
from starlette.testclient import TestClient
from pathlib import Path

from xpublish_file_metadata import FileMetadataPlugin

PREFIX = "datasets/geotiff/file-metadata"


@pytest.fixture(scope="module")
def hide_attrs() -> dict[str, list[str]]:
    """Return a dictionary of attributes to hide."""
    return {"geotiff": ["blockysize", "DERIVED_SUBDATASETS", "transform"]}


@pytest.fixture(scope="module")
def answers() -> dict[str, str]:
    """Return a dictionary of answers."""
    return {
        "driver": "GTiff",
        "dtype": "int16",
        "nodata": "None",
        "width": "53",
        "height": "25",
        "count": "2920",
        "crs": "None",
        "blockxsize": "53",
        "tiled": "False",
        "interleave": "pixel",
        "IMAGE_STRUCTURE": str(
            {
                "actual_range": "[185.16 322.1 ]",
                "dataset": "NMC Reanalysis",
                "GRIB_id": "11",
                "GRIB_name": "TMP",
                "level_desc": "Surface",
                "long_name": "4xDaily Air temperature at sigma level 995",
                "parent_stat": "Other",
                "precision": "2",
                "statistic": "Individual Obs",
                "units": "degK",
                "var_desc": "Air temperature",
            }
        ),
        "bounding_box": "BoundingBox(left=198.75, bottom=13.75, right=331.25, top=76.25)",
    }


@pytest.fixture(scope="module")
def geotiff_dataset() -> xr.Dataset:
    """Return a xarray dataset with a GeoTIFF source."""
    nc_ds = xr.tutorial.open_dataset("air_temperature")
    cache_dir = Path(nc_ds.encoding["source"]).parent

    tif_path = cache_dir / "air_temperature.tif"
    if not (tif_path).exists():
        nc_ds.air.rio.to_raster(tif_path)
    del nc_ds

    da = rioxarray.open_rasterio(tif_path)
    assert isinstance(da, xr.DataArray)

    ds = da.to_dataset(
        name="air_temperature",
        promote_attrs=True,
    )
    ds.encoding = da.encoding

    assert isinstance(ds, xr.Dataset)
    assert isinstance(ds.encoding["source"], str)
    assert ds.encoding["source"].endswith(".tif")
    return ds


@pytest.fixture(scope="module")
def xpublish_server(
    geotiff_dataset: xr.Dataset,
    hide_attrs: dict[str, list[str]],
) -> xpublish.Rest:
    """Return a TestClient instance with the FileMetadataPlugin."""
    server_obj = xpublish.Rest(
        {"geotiff": geotiff_dataset},
        plugins={"file_metadata": FileMetadataPlugin(hide_attrs=hide_attrs)},
    )
    return server_obj


@pytest.fixture(scope="module")
def client(xpublish_server: TestClient) -> TestClient:
    """Return a TestClient instance with the FileMetadataPlugin."""
    app = xpublish_server.app
    client = TestClient(app)
    return client


def test_geotiff_metadata(
    client: TestClient,
) -> None:
    """Test that the metadata is correct."""
    response = client.get(PREFIX)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "format" in response.json().keys()
    assert "attrs" in response.json().keys()


def test_geotiff_format(client: TestClient) -> None:
    """Test the format property."""
    response = client.get(f"{PREFIX}/format")
    assert response.status_code == 200
    assert response.json() == "geotiff"


def test_attrs(
    client: TestClient,
    answers: dict[str, str],
    hide_attrs: dict[str, list[str]],
) -> None:
    """Test the attrs property."""
    response = client.get(f"{PREFIX}/attrs")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json() == answers
    assert hide_attrs["geotiff"][0] not in response.json().keys()
    assert hide_attrs["geotiff"][1] not in response.json().keys()


def test_attr_names(
    client: TestClient,
    answers: dict[str, str],
    hide_attrs: dict[str, list[str]],
) -> None:
    """Test the attr_names property."""
    response = client.get(f"{PREFIX}/attr-names")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json() == list(answers.keys())
    assert hide_attrs["geotiff"][0] not in response.json()
    assert hide_attrs["geotiff"][1] not in response.json()


def test_single_attr(
    client: TestClient,
    answers: dict[str, str],
) -> None:
    """Test the single_attr property."""
    attr_name = list(answers.keys())[0]
    response = client.get(f"{PREFIX}/attrs/{attr_name}")
    assert response.status_code == 200
    assert isinstance(response.json(), str)
    assert response.json() == answers[attr_name]
