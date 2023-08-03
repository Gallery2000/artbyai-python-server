FROM python:3.9 as build-python

COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

FROM python:3.9-slim

COPY --from=build-python /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=build-python /usr/local/bin/ /usr/local/bin/
COPY . /app
WORKDIR /app

EXPOSE 5000
ENV PYTHONUNBUFFERED 1
ENV WERKZEUG_RUN_MAIN='true'
ENV TZ = 'Asia/Shanghai'

CMD ["gunicorn", "--bind", ":5000", "--workers", "1", "main:app"]