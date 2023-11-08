# CAPR Detailed Setup Process

This page will walk you through two ways to set up CAPR, starting from a new (or at least not-CAPR-running) Linux machine. (This may also work on Mac, but probably does not on Windows).

Remember that for either method, if you need to change the input lexicon or the template-aligned lexicon you will have to run that pipeline again before launching the program. These are the files found in the "server/pipeline" section, though you may need to investigate where they draw their current source lexicon from and where the output ends up to effectively replace them.

## Initial Setup: Pipelines and Input Files

CAPR will begin its work from an aligned input lexicon. This is a Wordlist that needs to have an `ID`, `DOCULECT`, `TOKENS`, `COGIDS`, and likely a `CONCEPT` for each row/entry. If your wordlist already has all of these columns, then great, you likely don't need to run it through the lexicon pipeline. One could start without any known cognates, however, as the Burmish data does. The lexicon pipeline then runs lexstat to generate possible cognates.

You can see examples of the full input format for both Burmish and Germanic in the `server/data` directory. 

#### Adding input data

All input lexicon files should be placed in the `server/data` directory so the program can find them. All files for a certain language will operate under a "pipeline" name. This means that *ALL* data files should be `pipeline_name-data.tsv` or some variation of this, where the pipeline name is what comes before the first `-` character (should be lowercase). You can also see examples of this in the existing data folder. 

#### Adding input FSTs

To begin making boards, CAPR needs a starting FST. This can, in fact, be a blank file (in which case we will get no boards to start). It must, however, exist in the `fsts/` directory as a text file, even if it is empty. The FST for any given pipeline should just be the name of that pipeline. For example, for both the `burmish` and `germanic` pipelines have FSTs with the name `burmish.txt` and `germanic.txt`. Language-specific transducers (since a pipeline is likely dealing with multiple languages) can be placed in the same file as Foma will just construct them all.

Please reference the existing FST files to see how different languages can be written and exported. Note that the exported names of each transducer should be the same name as the doculect found in the wordlist, but all lowercase.

Once you have your input FST and input data, you can start using CAPR.

**Important note:** If you are going to be starting from a blank FST, first open the CAPR interface and switch to the FST editor tab (top right button) before hitting "load" on your selected input data. Staying on the board tab may cause CAPR to break and you will have to reload the page.

## Method 1: Docker

If you do not already have Docker installed, install it! You can do so by following their instructions [here](https://docs.docker.com/desktop/) (for Docker Desktop, recommended if you don't know what you're doing) or [here](https://docs.docker.com/engine/install/) (for Docker Engine).

Second, edit the Caddyfile to point to the proper location. By default, the first line of the Caddyfile will be set to `:5000`, which will open CAPR on localhost:5000. If you are setting CAPR up to be run on a site or publicly facing from the Linux machine, you can change it (i.e. to the public IP of your machine, or the domain you want to host CAPR on).*

Lastly, rename the current `docker-compose.yml` to `docker-compose.debug.yml`, and rename the `docker-compose.prod.yml` to just `docker-compose.yml`. Now Docker will run the correct file when we launch it.

Now, run the provided docker-compose.yml using:
```
docker volume create caddy_data
docker compose build
docker compose up
```
Ta-da! You will now have CAPR up and running and ready for production use.

*Note that if you do change the Caddyfile to make it public facing, you'll need to add
`- 80:80` and  `- 443:443` to the `ports` section of the docker-compose.yml.

## Method 2: By Hand

For both production and development, CAPR uses Caddy to manage connecting the interface to the API (mostly avoiding CORS issues, and allowing for more flexibility overall). Before you start these instructions, please install [Caddy](https://caddyserver.com/). Follow the instructions they give for setting up, until the `caddy` command is available in your command line.

### For Production
If you would like to run the entire app at once (i.e. on a server or linux machine) so that you can use it, you can:

1. Make sure your Caddyfile is set to the location of the site you are using (i.e. a domain or simply `:5000` for personal use). This is the first line of the Caddyfile. See the example [Caddyfile](https://github.com/knightss27/capr/blob/main/Caddyfile) in this repository for *production* usage.
2. Start up the server and interface.
    ```
    cd server
    gunicorn server:app
    # starts api on :8000

    cd cognate-app
    npm i
    npm run build
    npm run start
    # starts interface on :8080
    ```

3. Run Caddy to handle proxying api requests.
    ```
    caddy adapt
    caddy run
    # opens interface at specified port
    ```

4. Visit the location you specified to use CAPR.

### For Development
If you want the ability to edit the code of the interface or the API while also testing the program, you can:

1. Begin the Python API using the development Docker file
    ```
    docker compose build
    docker compose up
    # opens API on localhost:5001
    ```

2. Start the interface (with Node >=14)
    ```
    cd cognate-app
    npm i
    npm run dev
    # opens interface on localhost:8080
    ```

3. Run Caddy to connect the interface and API.
    ```
    caddy run --config Caddyfile.dev
    # opens interface at specified port
    ```

*For development* your Caddyfile for development should look something like this:
```
:5002
# this can be any port that isn't taken or being used by the interface/api

route /api/* {
    uri strip_prefix /api
    reverse_proxy :5001
}

reverse_proxy :8080
```

If truly necessary (i.e. `:5001` and `:8080` are already in use), it is possible to change the ports of both the Flask and Svelte instances indivdually, but please reference their individual documentation.

### Installing FOMA and other issues

Remember that for the API to work you must have foma installed (*unless you are using Docker to run the API*).
```
sudo apt-get install libfoma0 libfoma0-dev
```

Do note that due to this [error](https://github.com/mhulden/foma/issues/97) it is possible that using the 0.9.18 version of foma you will end up with un-caught errors in FST compilation, that may end up returning a 500 error from the server. So, please be careful to check the version of the package your are installing with the above command. If you have problems on linux with the version, I strongly recommend just downloading and building the most recent version yourself:
```
~# wget https://github.com/mhulden/foma/archive/refs/heads/master.zip
~# unzip master.zip
~# cd ./foma-master/foma/
~/foma-master/foma# make <-- make sure to install the libraries listed below
~/foma-master/foma# make install 
```

I would love to have this working for other OS's that aren't linux distros, however getting foma to work with the Python bindings is, frankly, a complete mess (especially for Windows). I will say that one can successfully compile foma from source using Cygwin (using the 0.10.0 version on [Github](https://github.com/mhulden/foma)). Attempting to build the 0.9.18 version (whose source can be found [here](https://bitbucket.org/mhulden/foma/downloads/)) with more recent versions of gcc (what you will by default download with Cygwin), will throw errors.

If you attempt to build with Cygwin, note that you will likely need to edit the `Makefile` to remove the `-ltermcap` flag (as mentioned [here](http://damir.cavar.me/compiling-foma-on-windows-with-cygwin)). Also ensure that you install the `Devel` packages necessary for foma (`graphviz, flex, bison, zlib, libncurses-dev, libreadline-dev`).
