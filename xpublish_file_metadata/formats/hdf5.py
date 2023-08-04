import h5py
import cachey
import xarray as xr
from ..shared import FileMetadata


class Hdf5FileMetadata:
    """Get's file metadata for hdf5."""

    def get_file_metadata(
        self,
        dataset: xr.Dataset,
        cache: cachey.Cache,
        hide_attrs: list[str],
    ) -> FileMetadata:
        """Return the file metadata of the dataset."""
        raise NotImplementedError
