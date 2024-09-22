from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from auth import router as auth_router
from database import engine, Base
from starlette.middleware.sessions import SessionMiddleware
from starlette.config import Config
from starlette.templating import Jinja2Templates
config = Config('.env')
app = FastAPI()

# Create the database tables
Base.metadata.create_all(bind=engine)
app.add_middleware(SessionMiddleware, secret_key=config('SECRET_KEY'))
# Include authentication routes
app.include_router(auth_router, prefix="/auth")
templates = Jinja2Templates(directory="templates")
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Get the authorization token and user info from Okta
    

    return templates.TemplateResponse("login.html", {
        "request": request
    })
