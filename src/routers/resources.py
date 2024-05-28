import json

import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.database import get_db
from src.config import settings
from src.utils import segments_to_task
from datetime import datetime
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

    start_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    formatted_start_date = start_datetime.strftime('%Y%m%dT%H%M%S')

    end_datetime = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    time_diff_seconds = int((end_datetime - start_datetime).total_seconds())

    video_id = f"flux:tv:{channel}:{formatted_start_date}:{time_diff_seconds}"

    print(video_id)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch transcription data")
    data = json.loads(response.text)
    data['id'] = video_id

    return segments_to_task.convert(data, video_id)
