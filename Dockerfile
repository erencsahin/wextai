FROM python:3.12

ENV PYTHONBUFFERED=1

ENV PORT 8000

WORKDIR /app

COPY ./app/

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD gunicorn server.wsgi:application --bind 0.0.0.0:8000

EXPOSE 8000