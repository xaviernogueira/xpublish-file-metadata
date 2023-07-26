import cachey
import netCDF4 as nc
import xarray as xr
from pathlib import Path
from fastapi import Depends
from xpublish.utils.api import DATASET_ID_ATTR_KEY
from xpublish.dependencies import (
    get_dataset,
    get_cache,
)

from .shared import (
    NETCDF_DATASET_KEY,
    NETCDF_ATTRS_KEY,
)


def get_nc_dataset(
    dataset: xr.Dataset = Depends(get_dataset),
    cache: cachey.Cache = Depends(get_cache),
) -> nc.Dataset:
    """Return the netCDF4.Dataset object from an xarray.Dataset object."""

    # get the netcdf dataset from cache if cached
    cache_key = dataset.attrs.get(
        DATASET_ID_ATTR_KEY,
        '',
    ) + f'/{NETCDF_DATASET_KEY}'
    nc_dataset = cache.get(cache_key)

    # otherwise open the netcdf dataset and cache it
    if not nc_dataset:
        nc_path: Path = dataset.encoding['source']

        if not nc_path.suffx == '.nc':
            raise ValueError(f'Not a netCDF file: {nc_path}')

        nc_dataset = nc.Dataset(nc_path)
        cache.put(
            key=cache_key,
            value=nc_dataset,
            cost=99999,
        )

    return nc_dataset

# TODO: add more caching?
# TODO: figure out logging schema


def list_nc_attrs(
    nc_dataset: nc.Dataset = Depends(get_nc_dataset),
) -> list[str]:
    """Return a list of all netCDF attributes that can be accessed via the API."""
    return list(nc_dataset.ncattrs())


def get_nc_attr(
    attr_name: str,
    nc_dataset: nc.Dataset = Depends(get_nc_dataset),
) -> str:
    """Return the value of a netCDF attribute."""
    return str(nc_dataset.getncattr(attr_name))
