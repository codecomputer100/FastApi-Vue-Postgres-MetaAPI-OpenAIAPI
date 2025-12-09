# meta_api.py
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
import requests
from models import User
from database import get_db
from settings import settings
from openai import OpenAI

router = APIRouter(prefix="/meta", tags=["Meta"])

#-------------EndPoint Campaigns-------------------
#..................................................
@router.get("/campaigns")
def get_campaigns(request: Request, db: Session = Depends(get_db)):
    fb_user_id = request.cookies.get("fb_user_id")
    if not fb_user_id:
        raise HTTPException(status_code=401, detail="No autenticado (sin cookie)")

    user = db.query(User).filter_by(facebook_id=fb_user_id).first()
    if not user or not user.access_token:
        raise HTTPException(status_code=401, detail="No autenticado (sin token)")

    # 1) Obtener cuentas publicitarias del usuario
    act_url = f"https://graph.facebook.com/{settings.FB_API_VERSION}/me/adaccounts"
    act_params = {"fields": "id,account_id,name,account_status", "access_token": user.access_token}
    acc_resp = requests.get(act_url, params=act_params)
    acc_json = acc_resp.json()
    print("DEBUG adaccounts:", acc_json)

    if acc_resp.status_code != 200:
        raise HTTPException(status_code=400, detail={"where": "adaccounts", "resp": acc_json})

    accounts = acc_json.get("data", [])
    if not accounts:
        return {"campaigns": []}  # no tiene cuentas

    # 2) Para cada cuenta, traer campañas
    campaigns = []
    for acc in accounts:
        acc_id = acc["id"]  # form "act_XXXX"
        camp_url = f"https://graph.facebook.com/{settings.FB_API_VERSION}/{acc_id}/campaigns"
        camp_params = {
            "fields": "id,name,status,objective",
            "limit": 200,
            "access_token": user.access_token
        }
        camp_resp = requests.get(camp_url, params=camp_params)
        camp_json = camp_resp.json()
        print(f"DEBUG campaigns {acc_id}:", camp_json)

        if camp_resp.status_code != 200:
            # Si falla una, seguimos con las demás
            continue

        campaigns.extend(camp_json.get("data", []))
    return {"campaigns": campaigns}

#-------------EndPoint Campaigns Metrics-------------------
#..................................................

@router.get("/performance/{campaign_id}")
def get_campaign_performance(campaign_id: str, request: Request, db: Session = Depends(get_db)):
    fb_user_id = request.cookies.get("fb_user_id")
    if not fb_user_id:
        raise HTTPException(status_code=401, detail="No autenticado")

    user = db.query(User).filter_by(facebook_id=fb_user_id).first()
    if not user or not user.access_token:
        raise HTTPException(status_code=401, detail="Token no disponible")

    # Endpoint de insights
    url = f"https://graph.facebook.com/{settings.FB_API_VERSION}/{campaign_id}/insights"
    params = {
        "fields": "campaign_name,impressions,clicks,spend,ctr,cpc,cpm,actions",
        "date_preset": "last_year", #date_preset must be one of the following values: today, yesterday, this_month, last_month, this_quarter, maximum, data_maximum, last_3d, last_7d, last_14d, last_28d, last_30d, last_90d, last_week_mon_sun, last_week_sun_sat, last_quarter, last_year, this_week_mon_today, this_week_sun_today, this_year
        "access_token": user.access_token,
    }

    resp = requests.get(url, params=params)
    data = resp.json()

    print(f"DEBUG Performance [{campaign_id}]:", data)  # 👈 para ver en consola qué devuelve Meta

    # Si Meta devuelve un error
    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error"])

    insights = data.get("data", [])
    if not insights:
        # No hay datos, devolvemos respuesta vacía sin romper la app
        return {"performance": {"message": "Sin datos disponibles para este rango de fechas"}}

    metrics = insights[0]
    return {"performance": metrics}

#-------------EndPoint IA Campaigns Config Generation-------------------
#.......................................................................




# Inicializa el cliente de OpenAI
client = OpenAI(api_key=settings.OPENAI_API_KEY)

@router.post("/optimize")
async def optimize_campaign(data: dict, db: Session = Depends(get_db)):
    try:
        business_type = data.get("business_type")
        objective = data.get("objective")
        budget = data.get("budget")

        if not all([business_type, objective, budget]):
            raise HTTPException(status_code=400, detail="Faltan campos obligatorios.")

        # 🧠 Prompt plantilla
        prompt = f"""
        Eres un estratega experto en publicidad digital especializado en Meta Ads (Facebook e Instagram).

        Tu tarea es crear una **configuración de campaña óptima** para maximizar los resultados según los siguientes datos proporcionados por el usuario:
        - Rubro o industria del negocio: {business_type}
        - Objetivo principal de la campaña: {objective}
        - Presupuesto estimado total: {budget} USD

        Tu respuesta debe ser **exclusivamente un JSON válido**, sin texto adicional ni comentarios.
        La estructura del JSON debe ser la siguiente:

        {{
        "campaign_name": "Nombre de campaña sugerido según el rubro y objetivo",
        "objective": "Objetivo publicitario más adecuado según Meta (ej. LEAD_GENERATION, TRAFFIC, MESSAGES, SALES)",
        "recommended_budget_usd": "Monto sugerido diario o total (en USD)",
        "target_audience": {{
            "location": "País o ciudad sugerida",
            "age_range": "Ej. 25-45",
            "gender": "Todos / Hombres / Mujeres",
            "interests": ["lista de intereses relevantes según el rubro"],
            "behaviors": ["comportamientos o acciones relevantes"],
            "language": "Idioma principal"
        }},
        "ad_placement": {{
            "type": "Manual / Automático",
            "platforms": ["Facebook", "Instagram", "Audience Network", "Messenger"],
            "recommended_placements": ["Ej. Feed de Instagram, Historias de Facebook"]
        }},
        "optimization_event": "Evento de conversión óptimo (ej. Lead, Purchase, Link Click)",
        "ad_format": "Formato recomendado (ej. video, carrusel, imagen única)",
        "creative_recommendations": {{
            "headline": "Título atractivo recomendado",
            "primary_text": "Texto principal persuasivo",
            "cta": "Llamado a la acción sugerido (ej. Más información, Contáctanos, Comprar ahora)"
        }},
        "estimated_results": {{
            "reach": "Rango estimado de alcance (personas)",
            "ctr_expected": "Porcentaje estimado de clics (% CTR)",
            "cpl_expected": "Costo por lead o acción esperado en USD"
        }},
        "notes": "Consejos estratégicos adicionales (p. ej., duración óptima de campaña o recomendaciones de segmentación avanzada)"
        }}

        Sé preciso, coherente con las políticas publicitarias de Meta, y utiliza terminología real del administrador de anuncios.
        No devuelvas texto fuera del JSON.
        """


        # 🔥 Llama a GPT
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un experto en campañas de Meta Ads."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        result_text = response.choices[0].message.content.strip()

        # Intenta devolver JSON limpio
        import json
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            result = {"raw_response": result_text}

        return {"recommendation": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))