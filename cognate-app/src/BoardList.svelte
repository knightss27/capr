<script lang="ts">
    // Displays the list of boards, clickable at the top of the page.
    import type { Board } from "./types";
    import { currentBoard } from "./stores";

    export let boards: Board[];
</script>

<div>
    {#each boards as b, i}
    <span class:current={$currentBoard == b.id} on:click={() => {$currentBoard = b.id}}>{b.title}</span>
    {/each}
</div>

<style>
    div {
        max-width: 100%;
        display: flex;
        overflow-x: scroll;
        min-height: 3rem;
    }

    span {
        display: flex;
        cursor: pointer;
        flex-grow: 1;
        white-space: nowrap;
        margin: 0.1rem;
        padding: 0.25rem;
        background-color: lightgray;
        border-radius: 0.25rem;
    }

    span.current {
        color: white;
        background-color: dimgray;
    }
</style>