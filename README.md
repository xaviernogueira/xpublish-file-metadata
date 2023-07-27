# xpublish-netcdf

This package supplies two `xpublish` plugins for dealing with NetCDF files:
* `xpublish_netcdf.NetcdfRouterPlugin` - Provides `NetCDF4` library based metadata endpoints for hosted NetCDF files.
* `xpublish_netcdf.NetcdfProviderPlugin` - When given a dictionary of names and paths to local or cloud hosted NetCDF files, this plugin leverages `kerchunk` to increase read speed. Additionally, one can customize behavior (i.e., chunking scheme) via `kerchunk` kwargs.


