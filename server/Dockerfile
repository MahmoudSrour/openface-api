FROM bamos/openface

ADD . /src

RUN cd /src &&\
    apt-get update &&\
    pip install -r requirements.txt

EXPOSE 5000 80

RUN chmod -x /src/launch.sh
CMD sh /src/launch.sh