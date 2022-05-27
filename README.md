# CAPR: Computer Assisted Proto-language Reconstruction

This repository holds the re-write and working implementation of the interface and code for reconstructing Proto-Burmese, as found here:

> Xun Gong, & Nathan Hill. (2020). Materials for an Etymological Dictionary of Burmish. Zenodo. https://doi.org/10.5281/zenodo.4311182

To run while developing:

```
cd server
export FLASK_APP=capr
flask run
# opens API on localhost:5000
```
and
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
