from fastapi import FastAPI
from routes.users import router as users_router
from routes.chefs import router as chefs_router
from routes.bookings import router as bookings_router
from routes.reviews import router as reviews_router
from routes.dishes import router as dishes_router
from routes.pantry import router as pantry_router
from routes.favorites import router as favorites_router
from routes.memberships import router as memberships_router
from routes.availability import router as availability_router

app = FastAPI()

app.include_router(users_router)
app.include_router(chefs_router)
app.include_router(bookings_router)
app.include_router(reviews_router)
app.include_router(dishes_router)
app.include_router(pantry_router)
app.include_router(favorites_router)
app.include_router(memberships_router)
app.include_router(availability_router)

@app.get("/")
def home():
    return {"message": "Welcome to Chef Connection!"}