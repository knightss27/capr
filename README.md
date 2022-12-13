# CAPR: Computer Assisted Proto-language Reconstruction

This repository holds the re-write and working implementation of the interface and code for reconstructing Proto-Burmese, as found here:

> Xun Gong, & Nathan Hill. (2020). Materials for an Etymological Dictionary of Burmish. Zenodo. https://doi.org/10.5281/zenodo.4311182

To run while developing (with Python 3):

```
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

and then run Caddy to connect the interface and API.
```
caddy adapt
caddy run
# opens interface at specified port
```

You must have `libfoma0` and `libfoma0-dev` installed for the API to work.
```
sudo apt-get install libfoma0 libfoma0-dev
```

For much more in-depth instructions, see [SETUP.md]().

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
