FROM python:3.9-slim

WORKDIR /code

# 현재 도커파일이 상위폴더에 있는 docker-compose로 인해 수행되므로 상위폴더가 기준이 된다.
COPY ./backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./backend/app ./app/

EXPOSE 8000

CMD ["uvicorn","app.main:app", "--host","0.0.0.0", "--port", "8000", "--reload"]