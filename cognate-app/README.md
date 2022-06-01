# CAPR - Cognate Reassignment and FST Editor Interface

This is a Svelte app, no routing or anything else special.

### Development
```
npm i
npm run dev
# serves interface on localhost:8080
```

### Production Mode
```
npm run build
npm run start
# serves interface on localhost:8080 (production)
```

## Project Structure
```
.
├── public/
└── src/
    ├── menu/               - simple right-click menu component
    ├── App.sevlte          - central component
    ├── Board.svelte        - cognate board
    ├── BoardList.svelte    - header component for listing boards
    ├── Card.svelte         - cards for each word/gloss in columns
    ├── Column.svelte       - columns for words found on boards
    ├── FstComparator.sv... - fst editor wrapping component
    ├── FstEditor.svelte    - fst text editor, built with @codemirror
    ├── FstOutput.svelte    - fst comparison table
    └── FstReconstructio... - item of the comparison table
```