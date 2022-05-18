<script lang="ts">
    import type { Syllable, Word } from "./types";

    export let syllable: Syllable;
    export let word: Word;
</script>

<div class="word">
    <p class="word">
        {#each syllable.syllables as s, i}
            {#if i == syllable.syllOrder}
                <b>{s}</b>
            {:else}
                {s}
            {/if}
        {/each}
    </p>
    <p>
        {syllable.doculect}
    </p>
    <p>
        <i>{syllable.gloss}</i>
    </p>
</div>

<style>
    div {
        font-size: 0.75rem;
        margin: 0.25rem;
        padding: 0.5rem;
        border: 1px solid lightgray;
        border-radius: 0.5rem;
    }

    p {
        margin: 0px;
    }

    p.word {
        padding: 0.25rem 0.25rem;
        background-color: lightgray;
        border-radius: 0.25rem;
    }
</style>