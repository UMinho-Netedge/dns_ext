FROM python:3.9

RUN useradd -m -d /home/api coredns_api
RUN ["apt-get", "update"]
COPY ./ /home/api
USER coredns_api
ENV PATH="$PATH:/home/api/.local/bin"
RUN ["pip","install","-r","/home/api/requirements.txt"]

USER root
RUN ["chmod", "777", "/home/api/coredns/Corefile"]
RUN ["chmod", "777", "/home/api/coredns/zone0.db"]

USER coredns_api

ENTRYPOINT ["python3"]
CMD ["/home/api/main.py"]
