import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.database import get_db
from src.config import settings


router = APIRouter(tags=["resources"])


@router.get("/transcription")
def get_transcription(
                      plugin_name: str = Query('transcriptions'),
                      format: str = Query('amalia-mot'),
                      client_id: str = Query('transcriptions'),
                      channel: str = Query('TF1'),
                      start_date: str = Query('2022-1-25 20:0:0'),
                      end_date: str = Query('2022-1-25 20:30:0'),
                      db: Session = Depends(get_db)):

    base_url = settings.player_expert.base_url

    params = {
        'pluginName': plugin_name,
        'format': format,
        'clientId': client_id,
        'channel': channel,
        'startDate': start_date,
        'endDate': end_date,
    }

    params = {k: v for k, v in params.items() if v is not None}

    headers = {
        "Authorization": f"Bearer {settings.player_expert.token}"
    }

    response = requests.get(url=base_url, params=params, headers=headers, verify=settings.player_expert.verify_tls)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch transcription data")
    transcription_data = response.json()

    return transcription_data
