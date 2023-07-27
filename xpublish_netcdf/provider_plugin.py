import pydantic


class KerchunkKwargs(pydantic.BaseModel):
    # TODO: add more kwargs
    arg: str
