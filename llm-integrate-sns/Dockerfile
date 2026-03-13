FROM python:3.10.20-alpine AS base

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=8080

COPY ./app.py /app/app.py

EXPOSE 8080

CMD ["python", "app.py"]