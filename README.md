# CAPR: Computer Assisted Proto-language Reconstruction

This repository holds the re-write and working implementation of the interface and code for reconstructing Proto-Burmese, as found here:

> Xun Gong, & Nathan Hill. (2020). Materials for an Etymological Dictionary of Burmish. Zenodo. https://doi.org/10.5281/zenodo.4311182

To run while developing (with Python 3), follow these steps:
(Untested on Windows, works fine on Mac and Linux)

```
docker compose build
docker compose up
```

and then (with Node >=14)
```
cd cognate-app
npm i
npm run dev
# opens interface on localhost:8080
```

and then run Caddy to connect the interface and API.
```
caddy run --config Caddyfile.dev
# opens interface at specified port (5002 by default)
```

You must have `libfoma0` and `libfoma0-dev` installed for the API to work. **Note** that if you are using the docker container with the API (as you probably should), this shouldn't be a problem.
```
sudo apt-get install libfoma0 libfoma0-dev
```

## Important Notes

For much more in-depth instructions, see [SETUP.md](https://github.com/knightss27/capr/blob/update/SETUP.md).

For usage instructions, see [USAGE.md](https://github.com/knightss27/capr/blob/update/USAGE.md).

## Project Structure
```
.
├── cognate-app/
│   └── [svelte code for cognate reassignment and fst editor]
├── orthoprofiles/ *deprecated*
│   └── [orthographical profiles for pipeline stages]
├── pipeline/
│   └── [wordlist to tokenized lexicon, ran through lexstat to find intial cognates]
├── reconstruct/ *deprecated*
│   └── [intial fsts for pipeline usage]
└── server/
    └── [all api routes and associated functions]
```

You can read more about each individual folder in their respective READMEs.

## Citations

> List, J.-M. and R. Forkel (2022): LingRex: Linguistic Reconstruction with LingPy. [Computer software, Version 1.2.0]. Geneva: Zenodo. DOI: 10.5281/zenodo.1544943


> List, J.-M. and R. Forkel (2021): LingPy. A Python library for quantitative tasks in historical linguistics. Version 2.6.9. Max Planck Institute for Evolutionary Anthropology: Leipzig. https://lingpy.org


> Hulden, M. (2009). Foma: a finite-state compiler and library. In Proceedings of the 12th Conference of the European Chapter of the Association for Computational Linguistics (pp. 29–32).
