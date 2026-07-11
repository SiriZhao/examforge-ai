from fastapi import APIRouter

from app.config import settings

router = APIRouter(prefix="/api/saas", tags=["saas"])


@router.get("/config")
def public_saas_config() -> dict:
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "mode": settings.app_mode,
        "public_base_url": settings.public_base_url,
        "auth": {
            "provider": "supabase",
            "configured": settings.supabase_configured,
            "url": settings.supabase_url,
            "anon_key_available": bool(settings.supabase_anon_key),
        },
        "billing": {
            "provider": "stripe",
            "configured": settings.stripe_configured,
            "publishable_key_available": bool(settings.stripe_publishable_key),
        },
        "llm": {
            "server_provider_configured": settings.llm_server_configured,
            "default_provider": settings.default_llm_provider,
            "default_model": settings.default_llm_model,
        },
    }


@router.get("/plans")
def public_plans() -> dict:
    return {
        "currency": "usd",
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "monthly_price_cents": 0,
                "included_credits": 20,
                "features": ["Local safe draft", "Limited cloud jobs", "User-owned API key support"],
            },
            {
                "id": "student_plus",
                "name": "Student Plus",
                "monthly_price_cents": 900,
                "included_credits": 500,
                "features": ["AI deep review", "Long-document chunked synthesis", "Export pack history"],
            },
            {
                "id": "credit_pack_1000",
                "name": "Credit Pack 1000",
                "one_time_price_cents": 1200,
                "included_credits": 1000,
                "features": ["One-time usage top-up", "No subscription required"],
            },
        ],
    }

