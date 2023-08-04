import netCDF4
from fastapi import (
    APIRouter,
)
from xpublish import (
    Dependencies,
)


class NetcdfFileMetadata:
    """Get's file metadata for netcdf."""

    name: str = 'netcdf_file_metadata'
