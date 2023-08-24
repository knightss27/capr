<script lang="ts">
    import { onMount } from 'svelte';
	import BoardList from './BoardList.svelte';
	import Board from './Board.svelte';
	import { currentBoard } from './stores';
	import type { CognateApp, FstComparison } from './types';
	import { saveAs } from 'file-saver';
	
	// Imports starting JSON data for running as POC (proof of concept).
	// This data is a little too long, which is why HMR fails. Just reload the page manually.
	// @ts-ignore
	import initialData from './initialData2';
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
                syllables: loaded.syllables,
                fstDoculects: loaded.fstDoculects,
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

	let highestColNum = -1;
	const addNewColumn = () => {
		if (highestColNum == -1) {
			for (let num in loaded.columns) {
				let parsed = parseInt(num.substring(7))
				if (parsed > highestColNum) {
					highestColNum = parsed;
				}
			}
		}
		highestColNum += 1;
		let newColumn = `column-${highestColNum}`
		loaded.columns[newColumn] = {
			id: newColumn,
			syllableIds: []
		}
		loaded.boards[$currentBoard].columnIds.push(newColumn)
	}

	const saveBoardsLocally = () => {
		window.localStorage.setItem('boards', JSON.stringify({ boards: loaded.boards, columns: loaded.columns }));
	}

	const exportBoards = () => {
		const boardsToExport = {boards: loaded.boards, columns: loaded.columns};
		const blob = new Blob([JSON.stringify(boardsToExport)], { type: "application/json;charset=utf-8" });
		saveAs(blob, `capr-board-${new Date().toLocaleDateString()}.json`);
	}

	const saveFSTLocally = () => {
		window.localStorage.setItem('fsts', JSON.stringify({oldFst, newFst}));
	}

	const exportFST = () => {
		const fstToExport = "------------OLD FST:-------------\n" + oldFst + "\n------------NEW FST:-------------\n" + newFst;
		const blob = new Blob([fstToExport], { type: "text/plain" });
		saveAs(blob, `capr-fst-${new Date().toLocaleDateString()}.txt`);
	}

	let showCognateInterface = true;
	let showNewFst = false;

	// Whether or not we should use our new FST from the editor for refishing
	let useNewFst = false;

	let comparisonData: FstComparison = null;
	let selectedDoculects = [];
	let oldFst = "";
	let newFst = "";

	// Uploaded board management
	let files: FileList;
	$: if (files) {
		console.log(files)
		if (files[0] && files[0].type == "application/json") {
			const reader = new FileReader();
			reader.onload = (e: any) => {
				let newJSON = JSON.parse(e.target.result);
				loaded.columns = newJSON.columns;
				loaded.boards = newJSON.boards;
			};
			reader.readAsText(files[0])
		}
	}

    if (loaded.boards[$currentBoard] === undefined) {
        $currentBoard = loaded.currentBoard;
    }
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
			{:else}
				<button on:click={() => {showNewFst = !showNewFst}}>Switch FST</button>
				<span class="info">Current FST: {showNewFst ? "New" : "Old"}</span>
				<button on:click={saveFSTLocally}>Save FSTs</button>
				<button on:click={exportFST}>Export FSTs</button>
				<span class:statusError>Status: {statusMessage}</span>
			{/if}
			<span class="info sticky">Using source: <a href="/sources/{currentSourceFile}">{currentSourceFile}</a> (<a href="/sources/{currentSourceFile.substring(0, currentSourceFile.length-4)}-lexicon.{currentSourceFile.substring(currentSourceFile.length-3)}">lexicon</a>)</span>
			<button on:click={() => {showCognateInterface = !showCognateInterface}}>{showCognateInterface ? "Show FST Editor" : "Show Cognate Editor"}</button>
		</div>
		{#if showCognateInterface}
			<!-- The list of all possible boards -->
			<BoardList boards={Object.values(loaded.boards).sort((a, b) => a.title > b.title ? 1 : -1)} />
			<!-- The current board's title and some relevant options -->
			<div class="board-title">
				<h1>{loaded.boards[$currentBoard].title}</h1>
				<div class="options">
					Board Options:
					<button class="option" on:click={addNewColumn}>Add Column</button>
					<button class="option" on:click={saveBoardsLocally}>Save</button>
					<button class="option" on:click={exportBoards}>Export</button>
					<input accept="application/json" id="board-upload" type="file" bind:files/>
					<label for="board-upload" class="option custom-file-upload">
						Load
					</label>
				</div>
			</div>
			<!-- The Board component for displaying columns -->
			<Board columnIds={loaded.boards[$currentBoard].columnIds} columns={loaded.columns} bind:loaded {addNewColumn} />
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
		padding: 0px;
		margin: 0 auto;
		height: calc(100% - 8px);
	}

	div {
		display: flex;
		align-items: center;
		width: 100%;
		padding-bottom: 1rem;
	}

	div.board-title {
		justify-content: space-between;
	}

	div.options {
		width: fit-content;
		padding: 0px 1rem;
		background-color: #f4f4f4;
		border-radius: 0.5rem;
	}

	.option {
		border-radius: 0px;
		margin: 0px;
		padding: 0.5rem;
		border-top: none;
		border-bottom: none;
		cursor: pointer;
	}

	.option:first-child {
		border-left: 2px solid #ccc;
		margin-left: 1rem;
	}

	.option:last-child {
		border-right: 2px solid #ccc;
	}

	span {
		margin: auto 0.25rem;
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
		display: flex;
		border-radius: 0.5rem;
		margin: 0px 0.25rem;
	}

	.sticky {
		margin-left: auto !important;
	}

	input[type="file"] {
		display: none;
	}

	label.custom-file-upload {
		border-left: 1px solid #ccc;
	}
</style>