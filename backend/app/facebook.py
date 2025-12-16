"""Thin wrapper helpers for Facebook Graph API calls."""
import requests

GRAPH_BASE = "https://graph.facebook.com/v18.0"

def exchange_code_for_token(app_id: str, app_secret: str, redirect_uri: str, code: str):
    url = f"{GRAPH_BASE}/oauth/access_token"
    params = {
        "client_id": app_id,
        "redirect_uri": redirect_uri,
        "client_secret": app_secret,
        "code": code,
    }
    return requests.get(url, params=params, timeout=20).json()

def exchange_for_long_lived(app_id: str, app_secret: str, short_token: str):
    url = f"{GRAPH_BASE}/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_token,
    }
    return requests.get(url, params=params, timeout=20).json()

def get_pages(user_token: str):
    url = f"{GRAPH_BASE}/me/accounts"
    params = {"access_token": user_token}
    return requests.get(url, params=params, timeout=20).json()
