<script lang="ts">
    // Displays a board and all the columns
    import {default as ColumnComp}  from "./Column.svelte";
    import type { CognateApp, Column } from "./types";
    import  {dndzone } from "svelte-dnd-action";
    import { currentBoard } from "./stores";
    import Menu from "./menu/Menu.svelte";
    import MenuOption from "./menu/MenuOption.svelte";

    export let columnIds: string[];
    export let columns: { [key: string]: Column}
    export let loaded: CognateApp;
    // Callback for adding a new column
    export let addNewColumn: () => void;

    // Creates copies of our data for dragging and dropping, central state is only mutated on finalization
    let items = columnIds.map((c, i) => {return {id: i, name: c}});
    let columnItems = columnIds.map((c) => {return {id: c, items: columns[c].syllableIds.map(s => loaded.syllables[s])}})
    $: items = columnIds.map((c, i) => {return {id: i, name: c}});
    $: columnItems = columnIds.map((c) => {return {id: c, items: columns[c].syllableIds.map(s => loaded.syllables[s])}});

    // For dragging and dropping columns between each other (TODO: support dropping into one another)
    const handleConsider = (e) => {
        items = e.detail.items;
    }
    const handleFinalize = (e) => {
        items = e.detail.items;
        loaded.boards[$currentBoard].columnIds = e.detail.items.map(i => i.name);
    }

    // Handle dragging and dropping between columns, passed down to each column
    const handleColConsider = (id: string, e: any) => {
        let cIdx = columnItems.findIndex(c => c.id == id);
        columnItems[cIdx].items = e.detail.items;
        // console.log(e.detail.items)
        // console.log(columnItems[cIdx])
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
</script>

<div on:contextmenu|preventDefault={onRightClick} class="board" use:dndzone={{items: items, type: 'columns'}} on:consider={handleConsider} on:finalize={handleFinalize}>
    {#each items as c(c.id)}
    <ColumnComp column={columns[c.name]} syllables={loaded.syllables} fstUp={loaded.fstUp} words={loaded.words} handleConsider={handleColConsider} handleFinalize={handleColFinalize} bind:loaded bind:columnItems />
    {/each}
</div>

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
	}
</style>