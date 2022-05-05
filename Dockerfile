# set base image (host OS) as stage1
FROM python:3.9-buster as stage1

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies to the local user directory (eg. /root/.local)
RUN pip install --no-warn-script-location --user -r requirements.txt

# second unnamed stage
FROM python:3.9-slim-buster

# Install bluetooth packages
RUN apt-get update && apt-get install -y bluez

# set the working directory in the container
WORKDIR /code

# copy only the dependencies installation from the 1st stage image
COPY --from=stage1 /root/.local /root/.local

# copy the python scripts
COPY ./src/*.py ./

# update PATH environment variable
ENV PATH=/root/.local:$PATH

# command to run on container start
CMD [ "python", "./airthings-mqtt-ha.py" ]
