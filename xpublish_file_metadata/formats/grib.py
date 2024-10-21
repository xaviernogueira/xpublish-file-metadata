import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore", RuntimeWarning)
    try:
        import cfgrib
    except RuntimeError:
        raise ImportError
import xarray as xr
import cachey
from ..shared import FileMetadata


class GribFileMetadata:
    """Get's file metadata for grib."""

    def get_file_metadata(
        self,
        dataset: xr.Dataset,
        cache: cachey.Cache,
        hide_attrs: list[str],
    ) -> FileMetadata:
        """Return the file metadata of the dataset."""
        raise NotImplementedError
