FROM ubuntu:18.04
RUN echo "start build sprp..."

RUN mkdir /sprp-home
COPY . /sprp-home/
WORKDIR /sprp-home
RUN rm -rf /etc/apt/sources.list && cp ./docs/sources.list /etc/apt/

ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update && \
    apt-get install -y python3 python3-pip python3-dev \
    libgdal-dev \
    python3-pyproj python3-numpy python3-gdal \
    && pip3 install  setuptools

RUN pip3 install -e .

ENV SPRP_PORT 8000

ENTRYPOINT ["sprp-web"]