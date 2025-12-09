# auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import requests
from database import get_db
from models import User
from settings import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/login")
def login():
    fb_auth_url = (
        f"https://www.facebook.com/{settings.FB_API_VERSION}/dialog/oauth"
        f"?client_id={settings.FB_APP_ID}"
        f"&redirect_uri={settings.OAUTH_REDIRECT_URI}"
        f"&scope=ads_read,ads_management,business_management,pages_show_list,email"
    )
    return RedirectResponse(url=fb_auth_url)

@router.get("/callback")
def callback(code: str, db: Session = Depends(get_db)):
    # Intercambio code -> access_token
    token_url = f"https://graph.facebook.com/{settings.FB_API_VERSION}/oauth/access_token"
    params = {
        "client_id": settings.FB_APP_ID,
        "client_secret": settings.FB_APP_SECRET,
        "redirect_uri": settings.OAUTH_REDIRECT_URI,
        "code": code,
    }
    token_data = requests.get(token_url, params=params).json()
    access_token = token_data.get("access_token")
    expires_in = token_data.get("expires_in")

    if not access_token:
        raise HTTPException(status_code=400, detail=f"Sin token: {token_data}")

    # Datos del usuario
    me = requests.get(
        f"https://graph.facebook.com/{settings.FB_API_VERSION}/me",
        params={"fields": "id,name,email", "access_token": access_token}
    ).json()
    if "error" in me:
        raise HTTPException(status_code=400, detail=f"Error /me: {me}")

    # Guarda/actualiza en DB
    user = db.query(User).filter_by(facebook_id=me["id"]).first()
    if not user:
        user = User(
            facebook_id=me["id"],
            name=me.get("name"),
            email=me.get("email"),
            access_token=access_token,
            expires_in=expires_in,
        )
        db.add(user)
    else:
        user.access_token = access_token
        user.expires_in = expires_in
    db.commit()

    # Cookie con el facebook_id
    resp = RedirectResponse(url=f"{settings.FRONTEND_ORIGIN}/meta/campaigns")
    resp.set_cookie(
        key="fb_user_id",
        value=me["id"],
        httponly=True,
        samesite="Lax" if settings.FRONTEND_ORIGIN.startswith("http://") else "None",
        secure=not settings.FRONTEND_ORIGIN.startswith("http://"),
    )
    return resp

# Útil para probar que la cookie funciona
@router.get("/me")
def me(request, db: Session = Depends(get_db)):
    fb_user_id = request.cookies.get("fb_user_id")
    if not fb_user_id:
        raise HTTPException(status_code=401, detail="No autenticado (sin cookie)")
    user = db.query(User).filter_by(facebook_id=fb_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"name": user.name, "email": user.email, "facebook_id": user.facebook_id}
