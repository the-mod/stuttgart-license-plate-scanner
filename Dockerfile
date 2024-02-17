FROM python:3

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY scan_multiple_license_plates_telegram.py .
COPY images images

#CMD ["python", "scan_multiple_license_plates_telegram.py"]
ENTRYPOINT ["python", "scan_multiple_license_plates_telegram.py"]