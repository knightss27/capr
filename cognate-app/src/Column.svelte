<script lang="ts">
    // Displays a column and all of its words (or syllables as they are named)
    import Card from "./Card.svelte";
    import { dndzone } from "svelte-dnd-action";
    import { currentBoard } from "./stores";
    import type { CognateApp, Column, Syllable, Word } from "./types";

    export let fstUp: any;
    export let column: Column;
    export let syllables: { [key: string]: Syllable};
    export let words:  { [key: string]: Word}
    export let columnItems: { id: string, items: Syllable[]}[];
    export let loaded: CognateApp;
    // export let isShadow: boolean;

    export let handleConsider: (id: string, e: any) => void;
    export let handleFinalize: (id: string, e: any) => void;

    // Update the words in the column when we get a new column!
    let columnSyllables = column.syllableIds.map(s => syllables[s]);
    $: columnSyllables = column.syllableIds.map(s => syllables[s]);

    // Initialize reconstruction data
    let reconstructions: any = {};
    let crossid_reconstructions = [];

    // Generate the shared reconstructions, if any. Most of this is copied straight from Gong's code.
    const generateSharedReconstructions = () => {
        reconstructions = {};
        crossid_reconstructions = [];

        for (let syllable of columnSyllables) {
            if (syllable.doculect in fstUp) {
                let rec = fstUp[syllable.doculect][syllable.syllable];

                if (rec && rec.length) {
                    //   at_least_one = true;
                    if (!(syllable.doculect in reconstructions)) {
                        reconstructions[syllable.doculect] = new Set(rec);
                    } else {
                        reconstructions[syllable.doculect] = new Set([...reconstructions[syllable.doculect], ...rec]);
                    }
                }
            }
        }
        
        try {
            // @ts-ignore
            crossid_reconstructions = Array.from(Object.values(reconstructions).reduce((a, b) => new Set([...a].filter(x => b.has(x)))));
        } catch (e) {
            console.log(`No reconstructions for ${column.id}`)
        }
    }

    generateSharedReconstructions();

    let pastID = column.id;

    // Regenerate when a new board is selected (otherwise Svelte attempts to optimize too much of this)
    $: if ($currentBoard) {
        generateSharedReconstructions();
        console.log('calling generate')
    }

    // Regenerate after switching columns (otherwise we think we are a different column then we are supposed to be)
    $: if (column.id != pastID) {
        pastID = column.id;
        generateSharedReconstructions();
    }

</script>

<!-- {#if isShadow}
<span class="shadow"></span>
{:else} -->
<div class="column">
    <h3>
        {'*' + (column.syllableIds.length > 1 ? crossid_reconstructions.join(', ') : "")}
    </h3>
    <div class="dropzone" use:dndzone={{items: columnItems[columnItems.findIndex(c => c.id == column.id)].items}} on:consider={(e) => {handleConsider(column.id, e)}} on:finalize={(e) => {handleFinalize(column.id, e)}}>
        {#each columnItems[columnItems.findIndex(c => c.id == column.id)].items as syl(syl.id)}
        <Card syllable={syl} word={words[syl.wordId]} />
        {/each}
    </div>
</div>
<!-- {/if} -->



<style>
    div.column {
		display: flex;
		flex-direction: column;
		border: 1px solid gray;
		border-radius: 0.25rem;
		margin: 0 0.25rem;
        background-color: white;
        max-width: 10rem;
	}

    div.dropzone {
        min-height: 4rem;
    }

    h3 {
        margin: 0rem;
        padding: 0.25rem 0.5rem;
        border-bottom: 1px solid gray;
    }

    span.shadow {
        width: 4px;
        border: 2px solid blue;
    }
</style>