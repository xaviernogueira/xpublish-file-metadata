import logging
from typing import Sequence

import cachey
import xarray as xr
import fastapi
from starlette.responses import Response

import xpublish
from xpublish.utils.api import JSONResponse
from xpublish.utils.cache import CostTimer

from xpublish import (
    Dependencies,
    Plugin,
    hookimpl,
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
    ) -> fastapi.APIRouter:
        router = fastapi.APIRouter(
            prefix=self.dataset_router_prefix,
            tags=list(self.dataset_router_tags),
        )

        @router.get()
        def endpoint1():
            return Response('endpoint1')
