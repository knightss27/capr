<script lang="ts">
    // Displays the list of boards, clickable at the top of the page.
    import type { Board } from "./types";
    import { currentBoard } from "./stores";

    export let boards: Board[];
</script>

<div>
    <span class="title">Boards:</span>
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

    span.title {
        padding: 0.25rem 1rem; 
        position: sticky; 
        left: 0px; 
        margin: 0px; 
        padding: 0.35rem; 
        border: 1px solid black;
        border-top-right-radius: 0px;
        border-bottom-right-radius: 0px;
    }
</style>