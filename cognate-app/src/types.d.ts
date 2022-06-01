export interface CognateApp {
    boards: { [key: string]: Board},
    columns: { [key: string]: Column},
    currentBoard: string,
    fstIndex: any,
    maxColumn: number,
    searchColumns: any[],
    syllables: { [key: string]: Syllable},
    words: { [key: string]: Word},
    fstDoculects: any[],
    fstDown: any,
    fstUp: any,
}

export interface Board {
    id: string,
    title: string,
    columnIds: string[]
}

export interface Column {
    id: string,
    syllableIds: string[],
    protogloss?: string,
    refishingStatus?: string
}

export interface Syllable {
    id: string,
    doculect: string,
    gloss: string,
    glossid: string,
    syllOrder: number, //??
    syllable: string,
    syllables: string[],
    wordId: string
}

export interface Word {
    id: string,
    doculect: string,
    gloss: string,
    glossid: string,
    syllables: string[]
}

export interface FstComparison {
    chapters: {
        i: Section[],
        m: Section[],
        r: Section[],
        t: Section[]
    },
}

export interface Section {
    rows: {
        gloss: string,
        ipas: string[],
        new_reconstruction: string,
        new_reconstructions: string[],
        old_reconstruction: string,
        old_reconstructions: string[],
        status: string
    }[],
    title: string
}