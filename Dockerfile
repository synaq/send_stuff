FROM condaforge/miniforge3

RUN apt -y update

RUN mkdir -p /opt/project
RUN mkdir -p /opt/custom_python
COPY environment.yml /opt/custom_python
WORKDIR /opt/custom_python

RUN conda env create --prefix=/opt/custom_python/env
RUN echo "conda activate /opt/custom_python/env" >> /root/.bashrc

WORKDIR /opt/project

COPY . .

ENTRYPOINT ["/opt/custom_python/env/bin/python","main.py"]