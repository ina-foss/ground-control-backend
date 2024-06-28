FROM python:3.11

WORKDIR /code

COPY pip.conf /etc/pip.conf
COPY requirements.txt /code/requirements.txt
COPY requirements-dev.txt /code/requirements-dev.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt -r /code/requirements-dev.txt

COPY .. .

COPY ./alembic /code/alembic


CMD ["sh", "-c", "alembic upgrade head && python3 -m ina_ground_control.main"]


