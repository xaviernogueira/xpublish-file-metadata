# xpublish-netcdf
NEW PLAN: We can offer metadata for all non-Zarr compressed datatypes:
* NetCDF
* HDF5
* GeoTIFF
* GRIB

We will use ImportError schema to determine which metadata endpoints to offer.

This package supplies two `xpublish` plugins for dealing with compressed source files:
* `xpublish_netcdf.NetcdfRouterPlugin` - Provides `NetCDF4` library based metadata endpoints 
for hosted NetCDF files.

Later (should this be the same library?): 
* `xpublish_netcdf.NetcdfProviderPlugin` - When given a dictionary of names and paths to local or cloud hosted NetCDF files, this plugin leverages `kerchunk` to increase read speed. Additionally, one can customize behavior (i.e., chunking scheme) via `kerchunk` kwargs.


