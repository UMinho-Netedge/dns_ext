FROM python:3.9

# LABEL org.opencontainers.image.source="https://github.com/ATNOG/netedge-mep"

RUN useradd -m -d /home/api coredns_api
RUN ["apt-get", "update"]
COPY ./ /home/api
USER coredns_api
ENV PATH="$PATH:/home/api/.local/bin"
RUN ["pip","install","-r","/home/api/requirements.txt"]

ENTRYPOINT ["python3"]
CMD ["/home/netedge/main.py"]
