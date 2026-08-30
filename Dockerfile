FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    mono-runtime \
    mono-mcs \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m student

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/Data_Folder/Solutions_Folder && \
    chown -R student:student /app/Data_Folder/Solutions_Folder && \
    chmod 700 /app/Data_Folder

EXPOSE 5000

CMD ["python", "Sait_Logic_Folder/main.py"]