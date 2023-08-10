import rasterio
import cachey
import xarray as xr
from xpublish.utils.api import DATASET_ID_ATTR_KEY
from ..shared import (
    FileMetadata,
    FileFormats,
)


class GeoTiffFileMetadata:
    """Get's file metadata for geotiff."""

    format: FileFormats = 'geotiff'

    def __read_attrs(
        self,
        dataset: xr.Dataset,
        hide_attrs: list[str],
    ) -> dict:
        """Reads and combines the different rasterio attribute types."""
        with rasterio.open(dataset.encoding['source'], mode='r') as tiff:
            attrs = tiff.profile
            for i, tag in enumerate(tiff.tag_namespaces()):
                attrs[tag] = tiff.tags(i)
            attrs['bounding_box'] = str(tiff.bounds)

        for attr_name in list(attrs.keys()):
            if attr_name in hide_attrs:
                del attrs[attr_name]
            elif not isinstance(attrs[attr_name], str):
                attrs[attr_name] = str(attrs[attr_name])
        return attrs

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

        attrs_dict = cache.get(cache_key)

        if not attrs_dict:
            attrs_dict = self.__read_attrs(dataset, hide_attrs)

            cache.put(
                key=cache_key,
                value=attrs_dict,
                cost=99999,
            )
        # remove hidden attrs that may sneak in via cache
        else:
            for attr_name in hide_attrs:
                if attr_name in attrs_dict.keys():
                    del attrs_dict[attr_name]
        return FileMetadata(
            format=self.format,
            attrs=attrs_dict,
        )
