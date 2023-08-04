import logging
import pkg_resources
import cachey
import xarray as xr
from pydantic import BaseModel
from fastapi import (
    APIRouter,
    Depends,
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
)
from .shared import (
    FileFormats,
    EXTENSIONS_TO_FORMAT_KEY,
    FORMAT_WARNINGS,
)

logger: logging.Logger = logging.getLogger('uvicorn')


class FileMetadata(BaseModel):
    """File metadata model."""
    format: FileFormats
    attrs: dict[str, str]


@runtime_checkable
class FormatProtocol(Protocol):
    """Protocol for file metadata."""

    def get_file_metadata(
        self,
        dataset: xr.Dataset,
        cache: cachey.Cache,
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
        hide_attrs: Sequence[str] = None,
    ) -> None:
        super().__init__()
        if hide_attrs:
            self.__hide_attrs = list(hide_attrs)
        else:
            self.__hide_attrs = []

        self.__formats: dict[FileFormats, FormatProtocol] = load_file_formats()

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

        def get_metadata(
            dataset: Annotated[xr.Dataset, Depends(deps.get_dataset)],
        ) -> FileMetadata:
            """Gets and caches the metadata of the dataset."""
            raise NotImplementedError

        @router.get('/format')
        def get_file_format(
            dataset: Annotated[xr.Dataset, Depends(deps.get_dataset)],
        ) -> str:
            """Return the file format of the dataset."""
            raise NotImplementedError

        @router.get('/attrs')
        def get_attrs(
            dataset: Annotated[xr.Dataset, Depends(deps.get_dataset)],
        ) -> dict[str, str]:
            """Return the file attributes of the dataset."""
            raise NotImplementedError

        @router.get('/attrs/{attr_name}')
        def get_attr(
            attr_name: str,
            dataset: Annotated[xr.Dataset, Depends(deps.get_dataset)],
        ) -> str:
            """Return the file attribute of the dataset."""

            raise NotImplementedError

        return router
