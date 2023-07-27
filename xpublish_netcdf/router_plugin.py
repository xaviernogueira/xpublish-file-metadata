import logging
from typing import Sequence

import cachey
import xarray as xr
from fastapi import (
    Depends,
    Path,
    APIRouter,
    HTTPException,
)
from typing import (
    Sequence,
    Annotated,
)

from xpublish import (
    Dependencies,
    Plugin,
    hookimpl,
)

from .shared import (
    NETCDF_ATTRS_KEY,
)
from .router_utils import (
    get_nc_dataset,
    get_nc_attrs_dict,
    get_nc_attr,
)

logger = logging.getLogger('netcdf4_api')


class NetcdfRouterPlugin(Plugin):
    """Adds NetCDF4 based endpoints for datasets"""

    name: str = 'netcdf'

    dataset_router_prefix: str = '/netcdf'
    dataset_router_tags: Sequence[str] = ['netcdf']

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
            tags=list(self.dataset_router_tags),
        )

        @router.get(f'/{NETCDF_ATTRS_KEY}')
        def get_attr_values(
            dataset: Annotated[xr.Dataset, Depends(deps.dataset)],
            cache: Annotated[cachey.cache, Depends(deps.cache)],
        ) -> dict[str, str]:
            """Lists NetCDF attributes that can be accessed via the API."""
            nc_dataset = get_nc_dataset(dataset, cache)
            return get_nc_attrs_dict(
                dataset,
                cache,
                nc_dataset,
                self.hide_attrs,
            )

        @router.get(f'/{NETCDF_ATTRS_KEY}/names')
        def get_attr_names(
            dataset: Annotated[xr.Dataset, Depends(deps.dataset)],
            cache: Annotated[cachey.cache, Depends(deps.cache)],
        ) -> list[str]:
            """Lists NetCDF attributes that can be accessed via the API."""
            nc_dataset = get_nc_dataset(dataset, cache)
            nc_attrs = get_nc_attrs_dict(
                dataset,
                cache,
                nc_dataset,
                self.hide_attrs,
            )
            return list(nc_attrs.keys())

        @router.get(f'/{NETCDF_ATTRS_KEY}' + '/{name}')
        def get_single_attr(
            dataset: Annotated[xr.Dataset, Depends(deps.dataset)],
            cache: Annotated[cachey.cache, Depends(deps.cache)],
            name: str = Path(description='NetCDF attribute name to retrieve.'),
        ) -> str:
            """Returns the value of a NetCDF attribute."""
            nc_dataset = get_nc_dataset(dataset, cache)
            nc_attrs = get_nc_attrs_dict(
                dataset,
                cache,
                nc_dataset,
                self.hide_attrs,
            )

            if name not in nc_attrs:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f'NetCDF attribute not found: {name}! '
                        f'Use {self.dataset_router_prefix}/{NETCDF_ATTRS_KEY} '
                        f'to list available attributes.'
                    ),
                )
            return get_nc_attr(
                name,
                nc_attrs,
                self.hide_attrs,
            )
