from fastapi import FastAPI, HTTPException, Query, Path, status
from worker import GhanaPostGPS
from pydantic import BaseModel, Field
import logging
import uvicorn

logging.basicConfig(
    format="%(asctime)s - %(funcName)s -  %(levelname)s => %(message)s",
    level=logging.INFO,
    handlers=[
        logging.handlers.RotatingFileHandler(
            filename="../logs/app.log", mode="a", maxBytes=1000000, backupCount=5
        )
    ]
)

app = FastAPI()


class AddressDetails(BaseModel):
    street_name: str
    region: str
    district: str
    area: str
    post_code: str
    universal_address: str
    longitude: float
    latitude: float


@app.get("/details", response_model=AddressDetails, tags=["Address Details"])
def get_location(
    address: str = Query(title="The Address to be worked on.", example="GA-0591-9131")
):
    try:
        m = GhanaPostGPS()
        result = m.gps_to_loc(address)

        print(type(result))
        if not isinstance(result, dict):
            logging.error(f"Unable to get details for {result}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unable to retrieve details for {address}. Check and re-enter address.",
            )
        logging.info(f"Details for {address}: {result}")
        return result
    
    except Exception as err:
        logging.error(err)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unable to retrieve details for {address}. Check and re-enter address.",
        )


if __name__=="__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)