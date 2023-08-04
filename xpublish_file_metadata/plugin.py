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
    Sequence,
    Annotated,
)
from .shared import (
    FileFormat,
    EXTENSIONS_TO_FORMAT,
)

logger: logging.Logger = logging.getLogger('uvicorn')


class FileMetadata(BaseModel):
    """File metadata model."""
    format: FileFormat
    attrs: dict[str, str]


class FileMetadataPlugin(Plugin):
    """File metadata plugin for xpublish."""

    name: str = 'file-metadata'

    dataset_router_prefix: str = '/file-metadata'
    dataset_router_tags: Sequence[str] = ['file-metadata']

    def __init__(
        self,
        hide_attrs: Sequence[str] = None,
    ):
        super().__init__()
        if hide_attrs:
            self.__hide_attrs = list(hide_attrs)
        else:
            self.__hide_attrs = []

    @property
    def hide_attrs(self) -> list[str]:
        """List of NetCDF attributes to hide from the API."""
        return self.__hide_attrs

    @hookimpl
    def dataset_router(
        self,
        deps: Dependencies,
    ) -> APIRouter:

        router = APIRouter(
            prefix=self.dataset_router_prefix,
            tags=self.dataset_router_tags,
        )

        for entrypoint in pkg_resources.iter_entry_points('xpublish_file_metadata'):
            try:
                route_fn = entrypoint.load()
                route_fn(router, deps)

            except ImportError:
                logger.warning(f"Could not load entrypoint {entrypoint.name}")

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

        @router.get('/attrs/{attr}')
        def get_attr(
            attr: str,
            dataset: Annotated[xr.Dataset, Depends(deps.get_dataset)],
        ) -> str:
            """Return the file attribute of the dataset."""

            raise NotImplementedError

        return router
