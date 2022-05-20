<script lang="ts">
	import BoardList from './BoardList.svelte';
	import Board from './Board.svelte';
	import { currentBoard } from './stores';
	import type { CognateApp } from './types';
	
	// Imports starting JSON data for running as an example.
	// This data is a little too long, which is why HMR fails. Just reload the page manually.
	// @ts-ignore
	import initialData from './initialData';
	
	// Loads our initial data into a central state (TODO: think about extracting to a store)
	let loaded: CognateApp = {
		...initialData,
	} as unknown as CognateApp;

	let hasLoaded = false;

	const rootUrl = "localhost:3000"

	const handleRefish = async () => {
		const res = await fetch(`${rootUrl}/refish-board`, {
			method: 'POST',
			body: {
				columns: loaded.columns,
				boards: loaded.boards
			},
			
		})
	}
</script>


<main>
	{#if !hasLoaded}
		<button on:click={() => {hasLoaded = true}}>Load Board</button>
	{:else}
		<div>
			<button on:click={handleRefish}>Refish Board</button>
		</div>
		<!-- The list of all possible boards -->
		<BoardList boards={Object.values(loaded.boards)} />
		<!-- The current board's title -->
		<h1>{loaded.boards[$currentBoard].title}</h1>
		<!-- The Board component for displaying columns -->
		<Board columnIds={loaded.boards[$currentBoard].columnIds} columns={loaded.columns} bind:loaded />
	{/if}
</main>

<style>
	main {
		display: flex;
		flex-direction: column;
		width: 100%;
		height: 100%;
		padding: 0px;
		margin: 0 auto;
	}
</style>