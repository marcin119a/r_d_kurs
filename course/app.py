from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

#X_new = pd.DataFrame(
#   [[47, 'Łódź Bałuty', 2, True, 16.0, '6 dni temu']],
#   columns=['area_m2', 'locality', 'rooms', 'owner_direct', 'photos', 'date_posted']
#)
class PricePrediction(BaseModel):
    area_m2: float
    locality: str
    rooms: int
    owner_direct: bool
    photos: int
    date_posted: str


def predict_price(area_m2: float, locality: str, rooms: int, owner_direct: bool, photos: int, date_posted: str) -> float:
    X_new = pd.DataFrame(
        [[area_m2, locality, rooms, owner_direct, photos, date_posted]],
        columns=['area_m2', 'locality', 'rooms', 'owner_direct', 'photos', 'date_posted']
    )
    model = joblib.load("model_random_forest_adresowo_lodz.pkl")
    predicted_price = model.predict(X_new)
    return predicted_price[0]


app = FastAPI(title="Housing API")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Housing API"}

@app.post("/predict_price/")
async def predict(offer: PricePrediction):
    price = predict_price(
        area_m2=offer.area_m2,
        locality=offer.locality,
        rooms=offer.rooms,
        owner_direct=offer.owner_direct,
        photos=offer.photos,
        date_posted=offer.date_posted
    )
    return {"predicted_price": price}

@app.get("/train_model/")
async def train_model():
    from train import train_model
    r_2 = train_model()
    return {"message": "Model trained successfully with R²: {:.3f}".format(r_2)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)