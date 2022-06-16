# CAPR Detailed Setup Process

This page will walk you through two ways to set up CAPR, starting from a new (or at least not-CAPR-running) Linux machine.

## Method 1: Docker

If you do not already have Docker installed, install it! You can do so by following their instructions [here](https://docs.docker.com/desktop/) (for Docker Desktop) or [here](https://docs.docker.com/engine/install/) (for Docker Engine).

Second, edit the Caddyfile to point to the proper location. By default, the first line of the Caddyfile will be set to `:5000`, which will open CAPR on localhost:5000. If you are setting CAPR up to be run on a site or publicly facing from the Linux machine, you can change it (i.e. to the public IP of your machine, or the domain you want to host CAPR on). Note that if you do change the Caddyfile to make it public facing, you'll need to add
```
- 80:80
- 443:443
```
to the `ports` section of the docker-compose.yml.

Now, run the provided docker-compose.yml using:
```
docker volume create caddy_data
docker compose build
docker compose up
```
Ta-da! You will now have CAPR up and running and ready for production use.


## Method 2: By Hand

Coming soon...

