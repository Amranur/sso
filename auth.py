from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.config import Config
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from authlib.integrations.starlette_client import OAuth
from database import SessionLocal
from models import User

# Load config from .env
config = Config('.env')

# Register Okta OAuth client
oauth = OAuth(config)
oauth.register(
    name='okta',
    client_id=config('OKTA_CLIENT_ID'),
    client_secret=config('OKTA_CLIENT_SECRET'),
    authorize_url=f"{config('OKTA_ISSUER')}/v1/authorize",
    access_token_url=f"{config('OKTA_ISSUER')}/v1/token",
    client_kwargs={'scope': 'openid email profile'},
)

templates = Jinja2Templates(directory="templates")
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/okta/login", response_class=HTMLResponse)
async def login_page(request: Request):
    redirect_uri = request.url_for('auth_callback')
    return await oauth.okta.authorize_redirect(request, redirect_uri)

@router.get("/authorization-code/callback", response_class=HTMLResponse)
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    # Get the authorization token and user info from Okta
    token = await oauth.okta.authorize_access_token(request)
    user_info = token.get('userinfo')
    
    email = user_info['email']
    name = user_info['name']

    # Check if user already exists
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, name=name)
        db.add(user)
        db.commit()
        db.refresh(user)

    return templates.TemplateResponse("success.html", {
        "request": request,
        "name": name,
        "email": email
    })


