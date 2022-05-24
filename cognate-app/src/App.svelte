<script lang="ts">
	import BoardList from './BoardList.svelte';
	import Board from './Board.svelte';
	import { currentBoard } from './stores';
	import type { CognateApp } from './types';
	import FstEditor from './FstEditor.svelte';
	
	// Imports starting JSON data for running as POC (proof of concept).
	// This data is a little too long, which is why HMR fails. Just reload the page manually.
	// @ts-ignore
	import initialData from './initialData';
	import FstComparator from './FstComparator.svelte';
	
	
	// Loads our initial data into a central state (TODO: think about extracting to a store)
	let loaded: CognateApp = {
		...initialData,
	} as unknown as CognateApp;

	// Set hasLoaded to true while we are just testing for POC.
	let hasLoaded = true;

	// Status info for the top bar.
	let statusMessage = "Board loaded."
	let statusError = false;

	// Where our api is
	const rootUrl = "http://localhost:5000"

	// Handles the refish call
	const handleRefish = async () => {
		statusMessage = "Refishing current board..."
		await fetch(`${rootUrl}/refish-board`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify({
				columns: loaded.columns,
				boards: loaded.boards
			})
		})
			.then((res => res.json()))
			.then((data: any) => {
				// If we have our data, we should have refished correctly.
				console.log("Successfully refished.")
				loaded.columns = data.columns,
				loaded.boards = data.boards
				statusMessage = "Refishing completed."
			})
			.catch(e => {
				// If we have an error, we've got some issues.
				console.log("Error encountered while refishing:")
				console.error(e);
				statusError = true;
				statusMessage = e.message;
			})
	}

	let showNewFst = false;
	let showCognateInterface = false;
	let fstEditorWidth = 300;
</script>


<main>
	{#if !hasLoaded}
		<button on:click={() => {hasLoaded = true}}>Load Board</button>
	{:else}
		<div>
			{#if showCognateInterface}
				<button on:click={handleRefish}>Refish Board</button>
				<span class:statusError>Status: {statusMessage}</span>
			{:else}
				<button on:click={() => {showNewFst = !showNewFst}}>Switch FST</button>
				<span class="info">Current FST: {showNewFst ? "New" : "Old"}</span>
			{/if}
			<button class="sticky" on:click={() => {showCognateInterface = !showCognateInterface}}>{showCognateInterface ? "Show FST Editor" : "Show Cognate Editor"}</button>
		</div>
		{#if showCognateInterface}
			<!-- The list of all possible boards -->
			<BoardList boards={Object.values(loaded.boards)} />
			<!-- The current board's title -->
			<h1>{loaded.boards[$currentBoard].title}</h1>
			<!-- The Board component for displaying columns -->
			<Board columnIds={loaded.boards[$currentBoard].columnIds} columns={loaded.columns} bind:loaded />
		{:else}
			<FstComparator data={loaded} />
		{/if}
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

	div {
		display: flex;
		align-items: center;
		width: 100%;
		padding-bottom: 1rem;
	}

	div.editor-wrap {
		height: 100%;
		padding: 0px;
		max-width: 50%;
	}

	span {
		margin: auto 0.5rem;
		padding: 0.5rem 1rem;
		background-color: lightgreen;
		border-radius: 0.5rem;
	}

	span.info {
		background-color: #f4f4f4;
	}

	span.statusError {
		background-color: lightcoral;
	}

	button {
		margin: 0px;
		display: flex;
		border-radius: 0.5rem;
	}

	button.sticky {
		margin-left: auto;
	}
</style>