from typing import Literal

FileFormats: Literal = Literal[
    'netcdf',
    'hdf5',
    'geotiff',
    'grib',
]

EXTENSIONS_TO_FORMAT: dict[str, FileFormats] = {
    '.nc': 'netcdf',
    '.nc4': 'netcdf',
    '.nc3': 'netcdf',
    '.hdf': 'hdf5',
    '.tiff': 'geotiff',
    '.tif': 'geotiff',
    '.grib': 'grib',
}
