<script lang="ts">
	import BoardList from './BoardList.svelte';
	import Board from './Board.svelte';
	import { currentBoard } from './stores';
	import type { CognateApp, FstComparison } from './types';
	
	// Imports starting JSON data for running as POC (proof of concept).
	// This data is a little too long, which is why HMR fails. Just reload the page manually.
	// @ts-ignore
	import initialData from './initialData';
	import FstComparator from './FstComparator.svelte';
	
	// Loads our initial data into a central state (TODO: think about extracting to a store)
	let loaded: CognateApp = window.localStorage.getItem('boards') == null ? {
		...initialData,
	} as unknown as CognateApp : {
		...JSON.parse(window.localStorage.getItem('boards')),
		fstDoculects: initialData.fstDoculects,
		fstUp: initialData.fstUp,
		fstDown: initialData.fstDown,
		words: initialData.words,
		syllables: initialData.syllables,
	} as unknown as CognateApp;

	// Set hasLoaded to true while we are just testing for POC.
	let hasLoaded = true;

	// Status info for the top bar.
	let statusMessage = "Board loaded."
	let statusError = false;

	// Where our api is
	const rootUrl = "/api"
	// Just some info about the POC inputs
	const currentSourceFile = "burmish-primitive-2000-with-ob.tsv"

	// Handles the refish call
	const handleRefish = async () => {
		if (useNewFst && newFst.length == 0) {
			statusMessage = "No new FST loaded."
			statusError = true;
			return
		}
		
		statusError = false;
		statusMessage = "Refishing current boards..."
		
		await fetch(`${rootUrl}/refish-board`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify({
				columns: loaded.columns,
				boards: loaded.boards,
				transducer: useNewFst ? newFst : "internal"
			})
		})
			.then((res => res.json()))
			.then((data: any) => {
				// If we have our data, we should have refished correctly.
				console.log("Successfully refished.")
				loaded.columns = data.columns,
				loaded.boards = data.boards
				statusMessage = "Refishing completed."
				$currentBoard = "board-1";
			})
			.catch(e => {
				// If we have an error, we've got some issues.
				console.log("Error encountered while refishing:")
				console.error(e);
				statusError = true;
				statusMessage = e.message;
			})
	}

	const saveBoardsLocally = () => {
		window.localStorage.setItem('boards', JSON.stringify({ boards: loaded.boards, columns: loaded.columns }));
	}

	const saveFSTLocally = () => {
		window.localStorage.setItem('fsts', JSON.stringify({oldFst, newFst}));
	}

	let showCognateInterface = true;
	let showNewFst = false;

	// Whether or not we should use our new FST from the editor for refishing
	let useNewFst = false;

	let comparisonData: FstComparison = null;
	let selectedDoculects = [];
	let oldFst = "";
	let newFst = "";
</script>


<main>
	{#if !hasLoaded}
		<button on:click={() => {hasLoaded = true}}>Load Board</button>
	{:else}
		<div>
			{#if showCognateInterface}
				<button on:click={handleRefish}>Refish Board</button>
				<span class="info checkbox">
					<label for="useNewFst">Use new FST?</label>
					<input style="margin: 0px 0px 0px 0.25rem;" type="checkbox" name="useNewFst" bind:checked={useNewFst} />
				</span>
				<span class:statusError>Status: {statusMessage}</span>
				<button on:click={saveBoardsLocally}>Save Boards</button>
			{:else}
				<button on:click={() => {showNewFst = !showNewFst}}>Switch FST</button>
				<span class="info">Current FST: {showNewFst ? "New" : "Old"}</span>
				<button on:click={saveFSTLocally}>Save FSTs</button>
				<span class:statusError>Status: {statusMessage}</span>
			{/if}
			<span class="info sticky">Using source: <a href="/sources/{currentSourceFile}">{currentSourceFile}</a> (<a href="/sources/{currentSourceFile.substring(0, currentSourceFile.length-4)}-lexicon.{currentSourceFile.substring(currentSourceFile.length-3)}">lexicon</a>)</span>
			<button on:click={() => {showCognateInterface = !showCognateInterface}}>{showCognateInterface ? "Show FST Editor" : "Show Cognate Editor"}</button>
		</div>
		{#if showCognateInterface}
			<!-- The list of all possible boards -->
			<BoardList boards={Object.values(loaded.boards)} />
			<!-- The current board's title -->
			<h1>{loaded.boards[$currentBoard].title}</h1>
			<!-- The Board component for displaying columns -->
			<Board columnIds={loaded.boards[$currentBoard].columnIds} columns={loaded.columns} bind:loaded />
		{:else}
			<FstComparator data={loaded} {showNewFst} bind:oldFst bind:newFst bind:comparisonData bind:selectedDoculects bind:statusMessage bind:statusError />
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

	span.checkbox {
		display: flex;
		align-items: center;
		justify-content: space-between;
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

	.sticky {
		margin-left: auto !important;
	}
</style>