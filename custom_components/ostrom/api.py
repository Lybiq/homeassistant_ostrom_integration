from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, UTC, timedelta
from pathlib import Path

import aiohttp

from .const import API_BASES, AUTH_BASES, DEFAULT_ENDPOINT, DEFAULT_ENV

@dataclass
class OstromResult:
    ok: bool
    data: dict | None = None
    error: str | None = None
    status_code: int | None = None
    token_status_code: int | None = None

class OstromApi:
    def __init__(self, client_id: str, client_secret: str, zip_code: str, env: str = DEFAULT_ENV, endpoint: str = DEFAULT_ENDPOINT):
        self.client_id = client_id
        self.client_secret = client_secret
        self.zip_code = zip_code
        self.env = env
        self.endpoint = endpoint
        self.api_base = API_BASES.get(env.lower(), env.rstrip('/'))
        self.auth_base = AUTH_BASES.get(env.lower(), env.rstrip('/'))
        self.token_file = Path('/config/.storage/ostrom_token.json')

    def _load_cached_token(self):
        if not self.token_file.exists():
            return None
        try:
            data = json.loads(self.token_file.read_text())
            exp = data.get('expires_at')
            if not exp:
                return None
            if datetime.now(UTC) >= datetime.fromisoformat(exp):
                return None
            return data.get('access_token')
        except Exception:
            return None

    def _save_cached_token(self, token: str, expires_in: int):
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        expires_at = datetime.now(UTC) + timedelta(seconds=max(60, int(expires_in) - 60))
        self.token_file.write_text(json.dumps({'access_token': token, 'expires_at': expires_at.isoformat()}))

    async def _fetch_token(self, session: aiohttp.ClientSession) -> tuple[int, dict]:
        auth_url = self.auth_base + '/oauth2/token'
        auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
        async with session.post(auth_url, auth=auth, data={'grant_type': 'client_credentials'}, headers={'Accept': 'application/json'}) as resp:
            try:
                payload = await resp.json()
            except Exception:
                payload = {'text': await resp.text()}
            return resp.status, payload

    async def get_spot_prices(self, session: aiohttp.ClientSession) -> OstromResult:
        token = self._load_cached_token()
        if not token:
            token_status, token_json = await self._fetch_token(session)
            if token_status != 200 or 'access_token' not in token_json:
                return OstromResult(ok=False, error=token_json.get('detail') or token_json.get('type') or 'token request failed', status_code=None, token_status_code=token_status)
            token = token_json['access_token']
            self._save_cached_token(token, token_json.get('expires_in', 3600))
        url = self.api_base + self.endpoint
        headers = {'Accept': 'application/json', 'Authorization': f'Bearer {token}'}
        params = {'zipCode': self.zip_code, 'postalCode': self.zip_code}
        async with session.get(url, headers=headers, params=params) as resp:
            try:
                payload = await resp.json()
            except Exception:
                payload = {'text': await resp.text()}
            return OstromResult(ok=resp.status < 400, data=payload, status_code=resp.status)
