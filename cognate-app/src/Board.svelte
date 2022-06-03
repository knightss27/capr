<script lang="ts">
    // Displays a board and all the columns
    import {default as ColumnComp}  from "./Column.svelte";
    import type { CognateApp, Column } from "./types";
    import  {dndzone } from "svelte-dnd-action";
    import { currentBoard } from "./stores";
    import Menu from "./menu/Menu.svelte";
    import MenuOption from "./menu/MenuOption.svelte";
    import { tick } from "svelte";

    export let columnIds: string[];
    export let columns: { [key: string]: Column}
    export let loaded: CognateApp;
    // Callback for adding a new column
    export let addNewColumn: () => void;

    // Creates copies of our data for dragging and dropping, central state is only mutated on finalization
    let items = columnIds.map((c, i) => {return {id: i, name: c}});
    let columnItems = columnIds.map((c) => {return {id: c, items: columns[c].syllableIds.map(s => loaded.syllables[s])}})
    let pinnedItems = [];

    // Update items when we switch boards
    let prevBoard = $currentBoard;
    $: if ($currentBoard != prevBoard) {
        items = columnIds.map((c, i) => {return {id: i, name: c}});
        columnItems = [...pinnedItems.map((c) => {return {id: c.name, items: columns[c.name].syllableIds.map(s => loaded.syllables[s])}}), ...columnIds.map((c) => {return {id: c, items: columns[c].syllableIds.map(s => loaded.syllables[s])}})];
        prevBoard = $currentBoard;
    }

    // For dragging and dropping columns between each other (TODO: support dropping into one another)
    const handleConsider = (e) => {
        items = e.detail.items;
    }
    const handleFinalize = async (e) => {
        console.log('normal finalize', e.detail.items)
        items = e.detail.items;
        loaded.boards[$currentBoard].columnIds = e.detail.items.map(i => i.name);
        await tick();
        columnItems = [...pinnedItems.map((c) => {return {id: c.name, items: columns[c.name].syllableIds.map(s => loaded.syllables[s])}}), ...columnIds.map((c) => {return {id: c, items: columns[c].syllableIds.map(s => loaded.syllables[s])}})];
    }

    // Handle dragging and dropping between columns, passed down to each column
    const handleColConsider = (id: string, e: any) => {
        let cIdx = columnItems.findIndex(c => c.id == id);
        columnItems[cIdx].items = e.detail.items;
    }
    const handleColFinalize = (id: string, e: any) => {
        handleColConsider(id, e);
        loaded.columns[id].syllableIds = e.detail.items.map(i => i.id);
    }

    // Menu stuff
    let pos = { x: 0, y: 0 };
	let showMenu = false;
	async function onRightClick(e) {
		if (showMenu) {
			showMenu = false;
			await new Promise(res => setTimeout(res, 100));
		}
		
		pos = { x: e.clientX, y: e.clientY };
		showMenu = true;
	}
	function closeMenu() {
		showMenu = false;
	}

    // Handles dragging and dropping between the pinned section
    const handlePinnedConsider = (e: any) => {
        pinnedItems = e.detail.items.map((i) => {let c = i; c.id = "" + c.id; c.id = c.id.includes("pin") ? c.id : c.id+"-pin-"+$currentBoard; return c});
    }
    const handlePinnedFinalize = (e: any) => {
        pinnedItems = e.detail.items.map((i) => {let c = i; c.id = "" + c.id; c.id = c.id.includes("pin") ? c.id : c.id+"-pin-"+$currentBoard; return c});
    }

    // Handles deleting all pinned columns (and their items).
    const handlePinnedDelete = () => {
        let tempItems = pinnedItems;
        pinnedItems = [];
        for (let item of tempItems) {
            delete loaded.columns[item.id]
        }
        columnItems = [...pinnedItems.map((c) => {return {id: c.name, items: columns[c.name].syllableIds.map(s => loaded.syllables[s])}}), ...columnIds.map((c) => {return {id: c, items: columns[c].syllableIds.map(s => loaded.syllables[s])}})];
    }
</script>

<main>
<div on:contextmenu|preventDefault={onRightClick} class="board" use:dndzone={{items: items, type: 'columns'}} on:consider={handleConsider} on:finalize={handleFinalize}>
    {#each items as c(c.id)}
    <ColumnComp column={columns[c.name]} syllables={loaded.syllables} fstUp={loaded.fstUp} words={loaded.words} handleConsider={handleColConsider} handleFinalize={handleColFinalize} bind:loaded bind:columnItems />
    {/each}
</div>
<div class="pinned-wrapper">
    <div class="pinned-title">
        <span class="info">Pinned</span>
        <button on:click={handlePinnedDelete}>Delete</button>
    </div>
    
    <div class="pinned" use:dndzone={{items: pinnedItems, type: 'columns'}} on:consider={handlePinnedConsider} on:finalize={handlePinnedFinalize}>
        {#each pinnedItems as c(c.id)}
        <ColumnComp column={columns[c.name]} syllables={loaded.syllables} fstUp={loaded.fstUp} words={loaded.words} handleConsider={handleColConsider} handleFinalize={handleColFinalize} bind:loaded bind:columnItems />
        {/each}
    </div>
</div>
</main>

{#if showMenu}
	<Menu {...pos} on:click={closeMenu} on:clickoutside={closeMenu}>
		<MenuOption 
			on:click={addNewColumn} 
			text="Add Column" />
	</Menu>
{/if}

<style>
    div.board {
		display: flex;
        overflow-x: auto;
        max-width: 100%;
        min-height: fit-content;
        flex-grow: 1;
        padding-bottom: 1rem;
        overflow-y: hidden;
	}

    div.pinned {
        display: flex;
        width: 100%;
        height: 100%;
        overflow: auto;
    }

    div.pinned-wrapper {
        display: flex;
        flex-direction: column;
        width: 400px;
        border-left: 2px solid #ccc;
    }

    div.pinned-title {
        display: flex;
        margin-bottom: 0.5rem;
        padding: 0rem 0.25rem;
    }

    main {
        display: flex;
    }

    span {
		margin: 0px;
		padding: 0.5rem 1rem;
		background-color: #f4f4f4;
		border-radius: 0.5rem;
        flex-grow: 1;
	}

    button {
		display: flex;
		border-radius: 0.5rem;
		margin: 0px 0.25rem;
	}
</style>