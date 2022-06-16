FROM python:3.9-bullseye

WORKDIR /usr/app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update -y
RUN apt-get install -y wget unzip graphviz flex bison zlib1g libncurses-dev libreadline-dev

# Install this specific commit because it was before Foma broke their install process.
RUN wget https://github.com/mhulden/foma/archive/82f9acdef234eae8b7619ccc3a386cc0d7df62bc.zip
RUN unzip 82f9acdef234eae8b7619ccc3a386cc0d7df62bc.zip

WORKDIR "./foma-82f9acdef234eae8b7619ccc3a386cc0d7df62bc/foma/"
RUN make
RUN make install

WORKDIR "/usr/app"
COPY . .

CMD ["gunicorn",  "-b", "0.0.0.0:8000", "server:app"]