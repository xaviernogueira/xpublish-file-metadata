from typing import Literal


FileFormats: Literal = Literal[
    'netcdf',
    'hdf5',
    'geotiff',
    'grib',
]

EXTENSIONS_TO_FORMAT_KEY: dict[str, FileFormats] = {
    '.nc': 'netcdf',
    '.nc4': 'netcdf',
    '.nc3': 'netcdf',
    '.hdf': 'hdf5',
    '.tiff': 'geotiff',
    '.tif': 'geotiff',
    '.grib': 'grib',
}

FORMAT_WARNINGS: dict[FileFormats, str] = {
    'netcdf': 'Install netCDF4 to get file metadata for netcdf files.',
    'hdf5': 'Install h5py to get file metadata for hdf5 files.',
    'geotiff': 'Install rasterio to get file metadata for geotiff files.',
    'grib': 'Install cfgrib to get file metadata for grib files.',
}
