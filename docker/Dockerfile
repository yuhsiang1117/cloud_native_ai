FROM ollama/ollama:latest as ollama_server

# Keep apt cache to speed up subsequent builds
RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# Install common tools
RUN --mount=type=cache,target=/var/cache/apt,sharing=private \
    apt-get update && apt-get install -y \
    curl \
    git \
    sudo \
    usbutils \
    htop \
    wget \
    net-tools \
    tmux \
    vim \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN nohup bash -c "ollama serve &" \
    && sleep 5 \
    && ollama pull gemma4:e2b \
    && pkill ollama

RUN --mount=type=cache,target=/var/cache/apt,sharing=private \
    apt-get update && apt-get install -y \
    python3-pip \
    python3.12-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache/pip,sharing=private \
    pip install ollama

ENV TERM=xterm-256color

ENTRYPOINT []
CMD ["/bin/bash"]

FROM python:3.11-slim as discord_bot

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV TERM=xterm-256color

ENTRYPOINT []
CMD ["/bin/bash"]