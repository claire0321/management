FROM jenkins/inbound-agent:latest

USER root

# RUN apk add python3

# RUN apk add py3-pip pipx

# RUN python3 --version

RUN apt-get update && apt-get install ca-certificates curl && \
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc
    
USER jenkins