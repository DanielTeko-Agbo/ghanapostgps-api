
FROM python:3.10-slim

WORKDIR /var/www/html/GHPostAPI/

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

RUN /bin/bash -c "cd src/"

CMD ["uvicorn", "app:app", "--reload"]