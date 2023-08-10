FROM ubuntu:22.04
RUN apt update && apt install -y tor iproute2 curl netcat socat
ADD torrc /etc/tor/
WORKDIR /var/lib/tor
CMD ["tor"]
