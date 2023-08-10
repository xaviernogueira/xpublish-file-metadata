# xpublish-file-metadata

A simple `xpublish` plugin for serving metadata from the underlying files `xarray` is reading from.

**Note:** Zarr format metadata is already served by `xpublish` natively and is not handled by this plugin.

## Overview

* No unnecessary dependencies -> install only what you need for your use case (see [Installation](#installation)).
* File format agnostic endpoint paths:
  * `datasets/{dataset}/file-metadata` - returns all metadata of the underlying file.
  * `datasets/{dataset}/file-metadata/supported` - returns a list of all supported file formats with their respective sub-plugins installed.
  * `datasets/{dataset}/file-metadata/format` - returns the file format of the `xarray.Dataset` being served.
  * `datasets/{dataset}/file-metadata/attrs` - returns all metadata attributes of the underlying file (excludes file format).
  * `datasets/{dataset}/file-metadata/attr-names` - returns the names of all metadata attributes.
  * `datasets/{dataset}/file-metadata/attrs/{attr_name}` - returns the value of a single named attribute.

* Ability to hide certain metadata attributes (see [Hiding Attributes](#hiding-attributes)).

## Roadmap

* [x] Add support for `netcdf` files
* [x] Add support for `geotiff` files
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

Below are two examples using the `xpublish.Rest` syntax:

```python
import xpublish
from xpublish_file_metadata import FileMetadataPlugin

mock_dataset: xarray.Dataset = ...

# to hide "history" attributes from all file formats
xpublish.Rest(
    datasets={'my_data': mock_dataset},
    plugins=[
        FileMetadataPlugin(
            hide_attrs=['history'],
        ),
    ],
)

# to hide "history" attributes from netcdf files only
xpublish.Rest(
    datasets={'my_data': mock_dataset},
    plugins=[
        FileMetadataPlugin(
            hide_attrs={'netcdf': ['history']}
        ),
    ],
)
```

## Contributing

Contributions are welcome! We encourage you to open an issue or pull request if you have anything to request or add respectively.

* This project was developed using `poetry`. Start by installing `poetry` on your local machine, and use `poetry install` to install all dependencies.
* To run the test suite use `poetry run pytest`. Note that our `pytest` modules are located in the `tests` directory. Each can be ran individually (i.e., `poetry run pytest tests/test_2_netcdf.py`) if desired.
* We use `pre-commit` for formatting. To run the pre-commit hooks locally (recommended) use `poetry run pre-commit`.
* We encourage the use of [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/), which are simplified via the [VSCode extension](https://marketplace.visualstudio.com/items?itemName=vivaxy.vscode-conventional-commits).
* In your pull request, please include a description of your changes and a link to the issue(s) your changes addresses.
