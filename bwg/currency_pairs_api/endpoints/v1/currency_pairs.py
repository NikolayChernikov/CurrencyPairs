""" Test endpoint module. """
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from bwg.currency_pairs_api.services.currency_pairs import CurrencyPairsService
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

currency_pairs_router = APIRouter()


@currency_pairs_router.get(
    "/courses",
    tags=["Currency Pairs V1 - Services"],
    name="v1-currency-pairs",
)
@inject
async def get_currency_pairs(
        token: str,
        currency: str,
        currency_pairs: CurrencyPairsService = Depends(Provide["currency_pairs"])  # noqa
):
    res = currency_pairs.execute(token, currency)

    if not res:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Pair not found",
            }
        )
    return JSONResponse(res)
