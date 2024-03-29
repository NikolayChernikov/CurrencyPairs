""" Test endpoint module. """
from fastapi import APIRouter

router_test = APIRouter()


@router_test.get(
    "/test",
    tags=["Currency Pairs V1 - Services"],
    name="v1-test-endpoint",
)
async def get_test() -> dict:
    return {"status": "OK"}
