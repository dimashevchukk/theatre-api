FROM python:3.12-slim
LABEL maintainer="shevchukkdmytro@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN addgroup --system app && adduser --system --ingroup app my_user

RUN mkdir -p /files/static \
    && chown -R my_user:app /app /files \
    && chmod -R 755 /files

USER my_user

EXPOSE 8000
