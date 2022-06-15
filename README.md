# CAPR: Computer Assisted Proto-language Reconstruction

This repository holds the re-write and working implementation of the interface and code for reconstructing Proto-Burmese, as found here:

> Xun Gong, & Nathan Hill. (2020). Materials for an Etymological Dictionary of Burmish. Zenodo. https://doi.org/10.5281/zenodo.4311182

To run while developing (with Python 3):

```
pip install -r requirements.txt
cd server
export FLASK_APP=server
flask run
# opens API on localhost:5000
```
and then (with Node >=14)
```
cd cognate-app
npm i
npm run dev
# opens interface on localhost:8080
```

You must have `libfoma0` and `libfoma0-dev` installed for the API to work.
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

If you would like to run the entire app at once (i.e. on a server or linux machine) so that you can use it, please install [Caddy](https://caddyserver.com/). Follow the instructions they give for setting up, and once your `caddy` command is available, you can:

1. Make sure your Caddyfile is set to the location of the site you are using (i.e. a domain or simply `:5000` for personal use). This is the first line of the Caddyfile.
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

## Important Notes
When writing FSTs in the editor, you must write them for the languages below (unless you go ahead and change the code). Each language has a corresponding `.bin` name that it must be assigned at the end of that section of the transducer, i.e: `save stack lashi.bin`.

| Language Name | .bin Name |
| :------------ | :-------- |
| Old_Burmese | burmese.bin |
| Achang_Longchuan | ngochang.bin |
| Xiandao | xiandao.bin |
| Maru | maru.bin |
| Bola | bola.bin |
| Atsi | atsi.bin |
| Lashi | lashi.bin |


## Project Structure
```
.
├── cognate-app/
│   └── [svelte code for cognate reassignment and fst editor]
├── orthoprofiles/
│   └── [orthographical profiles for pipeline stages]
├── pipeline/
│   └── [wordlist to tokenized lexicon, ran through lexstat to find intial cognates]
├── reconstruct/
│   └── [intial fsts for pipeline usage]
└── server/
    └── [all api routes and associated functions]
```

You can read more about each individual folder in their respective READMEs.

## Citations

> List, J.-M. and R. Forkel (2022): LingRex: Linguistic Reconstruction with LingPy. [Computer software, Version 1.2.0]. Geneva: Zenodo. DOI: 10.5281/zenodo.1544943


> List, J.-M. and R. Forkel (2021): LingPy. A Python library for quantitative tasks in historical linguistics. Version 2.6.9. Max Planck Institute for Evolutionary Anthropology: Leipzig. https://lingpy.org


> Hulden, M. (2009). Foma: a finite-state compiler and library. In Proceedings of the 12th Conference of the European Chapter of the Association for Computational Linguistics (pp. 29–32).