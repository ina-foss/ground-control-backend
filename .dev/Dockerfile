FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

WORKDIR /code

COPY ../requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ../ /code

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
