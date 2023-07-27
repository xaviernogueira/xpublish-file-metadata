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
from xpublish.utils.api import JSONResponse

from xpublish import (
    Dependencies,
    Plugin,
    hookimpl,
)

from .shared import (
    NETCDF_ATTRS_KEY,
)
from .utils import (
    get_nc_dataset,
    list_nc_attrs,
    get_nc_attr,
)

logger = logging.getLogger('netcdf4_api')


class NetcdfPlugin(Plugin):
    """Adds NetCDF4 based endpoints for datasets"""

    name: str = 'netcdf'

    dataset_router_prefix: str = '/netcdf'
    dataset_router_tags: Sequence[str] = ['netcdf']

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
        def list_attrs(
            dataset: Annotated[xr.Dataset, Depends(deps.dataset)],
            cache: Annotated[cachey.cache, Depends(deps.cache)],
        ) -> list[str]:
            """Lists NetCDF attributes that can be accessed via the API."""
            nc_dataset = get_nc_dataset(dataset, cache)
            return list_nc_attrs(nc_dataset)

        @router.get(f'/{NETCDF_ATTRS_KEY}/json')
        def all_attr_values(
            dataset: Annotated[xr.Dataset, Depends(deps.dataset)],
            cache: Annotated[cachey.cache, Depends(deps.cache)],
        ) -> JSONResponse:
            """Lists NetCDF attributes that can be accessed via the API."""
            nc_dataset = get_nc_dataset(dataset, cache)
            nc_attrs = list_nc_attrs(nc_dataset)
            # TODO: have a utility function to do and cache this
            return JSONResponse(
                dict(
                    zip(
                        nc_attrs,
                        [get_nc_attr(attr, nc_dataset) for attr in nc_attrs],
                    ),
                ),
            )

        @router.get('/{name}')
        def get_single_attr(
            dataset: Annotated[xr.Dataset, Depends(deps.dataset)],
            cache: Annotated[cachey.cache, Depends(deps.cache)],
            name: str = Path(description='NetCDF attribute name to retrieve.'),
        ) -> str:
            """Returns the value of a NetCDF attribute."""
            nc_dataset = get_nc_dataset(dataset, cache)
            nc_attrs = list_nc_attrs(nc_dataset)

            if name not in nc_attrs:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f'NetCDF attribute not found: {name}! '
                        f'Use {self.dataset_router_prefix}/{NETCDF_ATTRS_KEY} '
                        f'to list available attributes.'
                    ),
                )
            return get_nc_attr(name, nc_dataset)
