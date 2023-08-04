# xpublish-file-metadata

A simple `xpublish` plugin for serving metadata from the underlying files `xarray` is reading from.

**Note:** Zarr format metadata is already served by `xpublish` natively and is not handled by this plugin.

## Overview

* No unnecessary dependencies -> install only what you need for your use case (see [Installation](#installation)).
* File format agnostic endpoint paths:
  * `datasets/{dataset}/file-metadata/supported` - returns a list of all supported file formats with their respective sub-plugins installed.
  * `datasets/{dataset}/file-metadata/format` - returns the file format of the `xarray.Dataset` being served.
  * `datasets/{dataset}/file-metadata/attrs` - returns all attributes of the underlying file.
  * `datasets/{dataset}/file-metadata/attr-names` - returns the names of all attributes.
  * `datasets/{dataset}/file-metadata/attrs/{attr_name}` - returns the value of a single named attribute.

* Ability to hide certain metadata attributes (see [Hiding Attributes](#hiding-attributes)).

## Roadmap

* [x] Add support for `netcdf` files (not fully tested)
* [ ] Add support for `geotiff` files
* [ ] Add support for `hdf5` files
* [ ] Add support for `zarr` files

## Installation

Since this plugin is split into multiple submodules (or sub-plugins, one for each file format), you can install only the parts you need. The drawback is that if you just install this library without any of the optional dependencies, the endpoints provided won't work.

To install the plugin without any file-format sub-plugins use:

```bash
pip install xpublish-file-metadata
```

We provide the the following dependency groups for ease of installation:

```bash
# for netcdf file support
pip install xpublish-file-metadata[netcdf]

# for geotiff file support
pip install xpublish-file-metadata[geotiff]

# for hdf5 file support
pip install xpublish-file-metadata[hdf5]

# for grib file support
pip install xpublish-file-metadata[grib]

# for support of any combination of the above
pip install xpublish-file-metadata[netcdf,geotiff,hdf5,grib]
```

## Hiding Attributes

For a variety of security reasons one may not want to expose all file metadata on a server. To hide certain attributes from being served, one can use the `hide_attrs` parameter when registering the plugin. This parameter can take either a list of strings attribute names to hide regardless of file format or a dictionary mapping file format names to a list of attribute names to hide for that file format.

```python
```
