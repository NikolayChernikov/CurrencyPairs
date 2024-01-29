""" Test endpoint module. """
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from src.currency_pairs_api.services.currency_pairs import CurrencyPairsService

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
) -> dict:
    res = currency_pairs.execute(token, currency)

    return res
