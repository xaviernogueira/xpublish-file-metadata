import netCDF4 as nc
from xpublish.utils.api import DATASET_ID_ATTR_KEY
import cachey
import xarray as xr
from ..shared import (
    FileMetadata,
    FileFormats,
)


class NetcdfFileMetadata:
    """Get's file metadata for netcdf."""
    format: FileFormats = 'netcdf'

    def __get_nc_dataset(
        self,
        dataset: xr.Dataset,
        cache: cachey.Cache,
    ) -> nc.Dataset:
        """Return the netCDF4.Dataset object from an xarray.Dataset object."""

        # get the netcdf dataset from cache if cached
        cache_key = dataset.attrs.get(
            DATASET_ID_ATTR_KEY,
            '',
        ) + f'/{self.format}/dataset'
        nc_dataset = cache.get(cache_key)

        # otherwise open the netcdf dataset and cache it
        nc_dataset = nc.Dataset(dataset.attrs['source'])
        cache.put(
            key=cache_key,
            value=nc_dataset,
            cost=99999,
        )

        return nc_dataset

    def get_file_metadata(
        self,
        dataset: xr.Dataset,
        cache: cachey.Cache,
        hide_attrs: list[str],
    ) -> FileMetadata:
        """Return the file metadata of the dataset."""
        cache_key = dataset.attrs.get(
            DATASET_ID_ATTR_KEY,
            '',
        ) + f'{self.format}/metadata'

        file_metadata = cache.get(cache_key)

        # protect against hidden attrs sneaking in via cache
        for attr_name in hide_attrs:
            if attr_name in file_metadata.attrs:
                del file_metadata.attrs[attr_name]

        if not file_metadata:
            nc_dataset = self.__get_nc_dataset(dataset, cache)

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

        return FileMetadata(
            format=self.format,
            attrs=attrs_dict,
        )
