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
from typing import (
    Annotated,
    Union,
)
from .shared import (
    NETCDF_DATASET_KEY,
    NETCDF_ATTRS_KEY,
)


def get_nc_dataset(
    dataset: Annotated[xr.Dataset, Depends(get_dataset)],
    cache: Annotated[cachey.Cache, Depends(get_cache)],
) -> nc.Dataset:
    """Return the netCDF4.Dataset object from an xarray.Dataset object."""

    # get the netcdf dataset from cache if cached
    cache_key = dataset.attrs.get(
        DATASET_ID_ATTR_KEY,
        '',
    ) + f'/{NETCDF_DATASET_KEY}/dataset'
    nc_dataset = cache.get(cache_key)

    # otherwise open the netcdf dataset and cache it
    if not nc_dataset:
        nc_path: Path = dataset.encoding['source']

        if not nc_path.suffix == '.nc':
            raise ValueError(f'Not a netCDF file: {nc_path}')

        nc_dataset = nc.Dataset(nc_path)
        cache.put(
            key=cache_key,
            value=nc_dataset,
            cost=99999,
        )

    return nc_dataset


def get_nc_attrs_dict(
    dataset: Annotated[xr.Dataset, Depends(get_dataset)],
    cache: Annotated[cachey.Cache, Depends(get_cache)],
    nc_dataset: Annotated[nc.Dataset, Depends(get_nc_dataset)],
    hide_attrs: list[str],
) -> dict[str, str]:
    """Return a list of all netCDF attributes that can be accessed via the API."""
    cache_key = dataset.attrs.get(
        DATASET_ID_ATTR_KEY,
        '',
    ) + f'/{NETCDF_DATASET_KEY}/dict'

    attrs_dict = cache.get(cache_key)

    # protect against hidden attrs sneaking in via cache
    for attr_name in hide_attrs:
        if attr_name in attrs_dict:
            del attrs_dict[attr_name]

    if not attrs_dict:
        nc_attr_names = [
            i for i in list(nc_dataset.ncattrs()) if i not in hide_attrs
        ]
        attrs_dict = dict(zip(
            nc_attr_names,
            [str(nc_dataset.getncattr(i)) for i in nc_attr_names],
        ))
        cache.put(
            key=cache_key,
            value=attrs_dict,
            cost=99999,
        )
    return attrs_dict


def get_nc_attr(
    attr_name: str,
    attrs_dict: Annotated[dict[str, str], Depends(get_nc_attrs_dict)],
    hide_attrs: list[str],
) -> str:
    """Return the value of a single netCDF attribute."""
    if attr_name in hide_attrs:
        raise ValueError(f'Invalid netCDF attribute: {attr_name}')
    return str(attrs_dict[attr_name])
