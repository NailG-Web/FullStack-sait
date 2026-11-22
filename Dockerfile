FROM ://microsoft.com AS dotnet-runtime

FROM python:3.10-slim

# Устанавливаем зависимости .NET и wget/unzip для скачивания PascalABC.NET
RUN apt-get update && apt-get install -y --no-install-recommends \
    libicu-dev \
    libssl3 \
    ca-certificates \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

COPY --from=dotnet-runtime /usr/share/dotnet /usr/share/dotnet
RUN ln -s /usr/share/dotnet/dotnet /usr/bin/dotnet

ENV DOTNET_ROOT=/usr/share/dotnet \
    DOTNET_CLI_HOME=/tmp/dotnet \
    DOTNET_NOLOGO=true \
    DOTNET_CLI_TELEMETRY_OPTOUT=1

RUN mkdir -p /opt/pabc && \
    wget -q https://pascalabc.net -O /tmp/pabc.zip && \
    unzip -q /tmp/pabc.zip -d /opt/pabc && \
    rm /tmp/pabc.zip

RUN useradd -m student

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/Data_Folder/Solutions_Folder && \
    chown -R student:student /app/Data_Folder/Solutions_Folder && \
    chmod 700 /app/Data_Folder

EXPOSE 5000

CMD ["python", "Sait_Logic_Folder/main.py"]