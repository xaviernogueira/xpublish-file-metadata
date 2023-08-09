import logging
import pkg_resources
import cachey
import xarray as xr
from pydantic import BaseModel
from pathlib import Path
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from xpublish import (
    Plugin,
    Dependencies,
    hookimpl,
)
from typing import (
    get_args,
    runtime_checkable,
    Sequence,
    Annotated,
    Protocol,
    Union,
)
from .shared import (
    FileFormats,
    FileMetadata,
    EXTENSIONS_TO_FORMAT_KEY,
    FORMAT_WARNINGS,
)

logger: logging.Logger = logging.getLogger('uvicorn')

@runtime_checkable
class FormatProtocol(Protocol):
    """Protocol for file metadata."""

    def get_file_metadata(
        self,
        dataset: xr.Dataset,
        cache: cachey.Cache,
        hide_attrs: list[str],
    ) -> FileMetadata:
        """Return the file metadata of the dataset."""
        ...


def load_file_formats() -> dict[FileFormats, FormatProtocol]:
    """Load in file format sub-plugins."""
    loaded_formats: dict[FileFormats, FormatProtocol] = {}

    for entrypoint in pkg_resources.iter_entry_points('xpublish_file_metadata.formats'):
        try:
            metadata_grabber = entrypoint.load()
            if not entrypoint.name in get_args(FileFormats):
                logger.warning(
                    f'Skipping {entrypoint.name} support: Not a supported file format.'
                )
                continue
            if not isinstance(metadata_grabber, FormatProtocol):
                logger.warning(
                    f'Skipping {entrypoint.name} support: Plugin does not match protocol.'
                )
                continue

            loaded_formats[entrypoint.name] = metadata_grabber

        except ImportError:
            logger.warning(
                f'ImportError: {FORMAT_WARNINGS[entrypoint.name]}'
            )
    return loaded_formats


class FileMetadataPlugin(Plugin):
    """File metadata plugin for xpublish."""

    name: str = 'file-metadata'

    dataset_router_prefix: str = '/file-metadata'
    dataset_router_tags: Sequence[str] = ['file-metadata']

    def __init__(
        self,
        hide_attrs: Union[list[str], dict[FileFormats, list[str]]] = None,
    ) -> None:
        super().__init__()

        self.__formats: dict[FileFormats, FormatProtocol] = load_file_formats()

        self.__hide_attrs: dict[FileFormats, list[str]] = {}
        if not hide_attrs:
            hide_attrs = {}
        for format in self.loaded_formats.keys():
            if isinstance(hide_attrs, list):
                self.__hide_attrs[format] = list(hide_attrs)
            elif isinstance(hide_attrs, dict):
                self.__hide_attrs[format] = hide_attrs.get(format, [])

    @property
    def hide_attrs(self) -> dict[FileFormats, str]:
        """A List of attributes to hide from the API for each file format"""
        return self.__hide_attrs

    @property
    def loaded_formats(self) -> dict[FileFormats, FormatProtocol]:
        """Dictionary of loaded file formats."""
        return self.__formats

    @hookimpl
    def dataset_router(
        self,
        deps: Dependencies,
    ) -> APIRouter:

        router = APIRouter(
            prefix=self.dataset_router_prefix,
            tags=self.dataset_router_tags,
        )

        @router.get('/supported')
        def supported_formats() -> list[str]:
            """Shows which file formats have metadata support.

            NOTE: This depends on which optional dependencies are installed!
            """
            return list(self.loaded_formats.keys())

        @router.get('/format')
        def file_format(
            dataset: Annotated[xr.Dataset, Depends(deps.dataset)],
        ) -> str:
            """Return the file format of the dataset.

            NOTE: This is not the precise format, but rather the format key
            in relationship to the xpublish-file-metadata plugin.
            """
            extension = Path(dataset.encoding['source']).suffix
            try:
                return EXTENSIONS_TO_FORMAT_KEY[extension]
            except KeyError:
                raise KeyError(
                    f'File format not supported: {extension}'
                )
        
        @router.get('/')
        def metadata(
            dataset: Annotated[xr.Dataset, Depends(deps.dataset)],
            cache: Annotated[cachey.Cache, Depends(deps.cache)],
        ) -> FileMetadata:
            """Gets and caches the metadata of the dataset."""
            format_key = file_format(dataset)
            grabber: FormatProtocol = self.loaded_formats[format_key]()
            return grabber.get_file_metadata(
                dataset=dataset,
                cache=cache,
                hide_attrs=self.hide_attrs[format_key],
            )

        @router.get('/attrs')
        def attrs(
            dataset: Annotated[xr.Dataset, Depends(deps.dataset)],
            cache: Annotated[cachey.Cache, Depends(deps.cache)],
        ) -> dict[str, str]:
            """Return the file attributes of the dataset."""
            return metadata(dataset, cache).attrs

        @router.get('/attr-names')
        def attr_names(
            dataset: Annotated[xr.Dataset, Depends(deps.dataset)],
            cache: Annotated[cachey.Cache, Depends(deps.cache)],
        ) -> list[str]:
            """Return the file attribute names of the dataset."""
            return list(
                metadata(
                    dataset,
                    cache,
                ).attrs.keys()
            )

        @router.get('/attrs/{attr_name}')
        def single_attr(
            attr_name: str,
            dataset: Annotated[xr.Dataset, Depends(deps.dataset)],
            cache: Annotated[cachey.Cache, Depends(deps.cache)],
        ) -> str:
            """Return the file attribute of the dataset."""

            attrs = metadata(dataset, cache).attrs
            try:
                return attrs[attr_name]
            except KeyError:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f'Attribute not found: {attr_name}! '
                        f'Use {self.dataset_router_prefix}/attr-names '
                        f'to list available attributes.'
                    ),
                )

        return router
