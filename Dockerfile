FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip \
    ca-certificates \
    libicu-dev \
    libssl3 \
    && wget -q https://microsoft.com -O /tmp/packages-microsoft-prod.deb \
    && dpkg -i /tmp/packages-microsoft-prod.deb \
    && rm /tmp/packages-microsoft-prod.deb \
    && apt-get update \
    && apt-get install -y --no-install-recommends dotnet-runtime-10.0 \
    && rm -rf /var/lib/apt/lists/*

ENV DOTNET_NOLOGO=true \
    DOTNET_CLI_TELEMETRY_OPTOUT=1 \
    DOTNET_GCHeapHardLimit=0x10000000

RUN mkdir -p /opt/pabc && \
    wget -q https://pascalabc.net -O /tmp/pabc.zip && \
    unzip -q /tmp/pabc.zip -d /opt/pabc && \
    rm /tmp/pabc.zip

RUN echo '{"runtimeOptions":{"tfm":"net10.0","framework":{"name":"Microsoft.NETCore.App","version":"10.0.0"}}}' > /opt/pabc/pabc.runtimeconfig.json

RUN useradd -m student

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/Data_Folder/Solutions_Folder && \
    chown -R student:student /app/Data_Folder/Solutions_Folder && \
    chmod 700 /app/Data_Folder

EXPOSE 5000

CMD ["python", "Sait_Logic_Folder/main.py"]