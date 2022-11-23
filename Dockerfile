FROM python:3.9

USER root

RUN ["apt-get", "update"]
COPY ./ /home/api

ENV PATH="$PATH:/home/api/.local/bin"
RUN ["pip","install","-r","/home/api/requirements.txt"]

ENTRYPOINT ["python3"]
CMD ["/home/api/main.py"]
