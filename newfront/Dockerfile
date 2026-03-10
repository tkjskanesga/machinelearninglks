FROM python:3.10.20-alpine AS base

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Flask Config
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000
ENV FLASK_DEBUG=true

COPY ./app.py /app/app.py
COPY ./templates /app/templates

EXPOSE 5000

CMD ["python", "app.py"]