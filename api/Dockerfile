FROM python:3.10

RUN mkdir -p ~/.postgresql && \
wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" \
    --output-document ~/.postgresql/root.crt && \
chmod 0600 ~/.postgresql/root.crt

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:443", "main:app", "--certfile=/etc/api-certificate/certificate.crt", "--keyfile=/etc/api-certificate-key/certificate.key"]

# CMD ["python", "main.py"]
