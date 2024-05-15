import json

import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.database import get_db
from src.config import settings
from src.utils import segments_to_task

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

    video_id = f"flux:tv:{params['channel']}:{params['startDate'][:4]}{params['startDate'][5:7]}{params['startDate'][8:10]}T{params['startDate'][11:13]}{params['startDate'][14:16]}:{params['endDate'][11:13]}{params['endDate'][14:16]}"

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch transcription data")
    data = json.loads(response.text)
    data['id'] = video_id

    return segments_to_task.convert(data, video_id)
