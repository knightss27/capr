<script lang="ts">
    import FstEditor from "./FstEditor.svelte";
    import Select from "svelte-select";
    import type { CognateApp, FstComparison } from "./types";
    // import initialTransducers from "./initialTransducers"
    import FstOutput from "./FstOutput.svelte";
    import { Circle2 } from "svelte-loading-spinners";

    export let data: CognateApp;
    export let showNewFst = false;
    export let statusMessage: string;
    export let statusError: boolean;
    export let oldFst: string = "";
    export let newFst: string = "";

    // Temporarily set our FSTs to existing options for testing.
    if (window.localStorage.getItem('fsts') != null) {
        let fsts = JSON.parse(window.localStorage.getItem('fsts'));
        oldFst = fsts.oldFst;
        newFst = fsts.newFst;
    }


    // Doculects to be selected from.
    $: doculects = ['Debug', ...data.fstDoculects];

    // Currently selected doculect list.
    export let selectedDoculects = [];

    // TODO: move this to just replace call
    let rootUrl = "/api"

    export let handleDebugComparison = async () => {};

    // Calls the comparison route with our FSTs, returning the new data.
    const handleComparison = async () => {
        if (selectedDoculects.map(f => f.value).includes('Debug')) {
            console.log("Running debug rerun")
            await handleDebugComparison();
        } else {
            statusMessage = "Calculating correspondence patterns..."
            comparisonData = null;
            loadingData = true;
            statusError = false;
            compilerErrors = [];

            fetch(`${rootUrl}/compare-fst`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    langsUnderStudy: selectedDoculects.map(p => p.value),
                    oldTransducer: oldFst,
                    newTransducer: newFst,
                    board: {
                        columns: data.columns,
                        boards: data.boards
                    }
                })
            })
            .then(res => res.json())
            .then(data => {
                // If we have our data, we should have calculated correctly.
                console.log("Successfully calculated correspondence.")
                comparisonData = data;
                statusMessage = "Patterns calculated."
                statusError = false;
                if (data.missing_transducers.length > 0) {
                    statusMessage += " Missing FSTs: " + data.missing_transducers.join(",");
                }
                if (data.errors.length > 0) {
                    compilerErrors = data.errors;
                }
                loadingData = false;
            })
            .catch(e => {
                // If we have an error, we've got some issues.
                console.log("Error encountered while calculating correspondence:")
                console.error(e);
                statusError = true;
                statusMessage = e.message;
                loadingData = false;
            })
        }
    }

    // Holds the data returned by the `compare-fst` route
    export let comparisonData: FstComparison = null;
    let loadingData = false;
    // Lets us keep the editor widths the same when switching between new/old
	let fstEditorWidth = 600;
    // Keep track of `foma` compiling errors.
    let compilerErrors: string[] = [];

</script>


<main>
    <!-- Both of the FST editors, which are CodeMirror 6 instances -->
    <div class="editor">
        {#if showNewFst}
        <FstEditor bind:fst={newFst} id={1} bind:fstEditorWidth {oldFst} />
        {:else}
        <FstEditor bind:fst={oldFst} id={2} bind:fstEditorWidth />
        {/if}
    </div>
    <!-- The compare list, which is a massive table with a Select at the top -->
    <div class="compare">
        <div class="compare-list">
            <!-- Select component from @svelte-select -->
            <Select placeholder="Select languages" placeholderAlwaysShow={true} items={doculects} isMulti={true} bind:value={selectedDoculects} />
            <button on:click={handleComparison}>Go</button>
        </div>
        {#if compilerErrors.length > 0}
            {#each compilerErrors as err}
            <span class="compiler-error">{err}</span>
            {/each}
        {/if}
        {#if comparisonData}
            <FstOutput data={comparisonData} langsUnderStudy={selectedDoculects.map(p => p.value)} />
        {:else if loadingData}
            <div class="loader">
                <Circle2 />            
            </div>
        {/if}
        {#if selectedDoculects && selectedDoculects.map(f => f.value).includes('Debug')}
            <div style="max-height: 100%; overflow-y: scroll;">
                {#each Object.entries(data.fstUp) as [language, words]}
                <h1>{language}</h1>
                <table class="debug-table" cellpadding="0" cellspacing="0">
                    <tr><th>Word/Syllable</th><th>Apply Up</th></tr>
                    {#each Object.entries(words) as [word, applied]}
                    <tr><td>{word}</td><td>{applied.join(", ")}</td></tr>
                    {/each}
                </table>
                {/each}
            </div>
        {/if}
    </div>
</main>

<style>
    main {
        width: 100%;
        height: calc(100vh - 70px);
        display: flex;
    }

    div {
        /* display: flex; */
    }

    div.editor {
        display: flex;
    }

    div.compare {
        display: flex;
        flex-direction: column;
        width: 100%;
    }

    div.compare-list {
        display: flex;
        width: 100%;
        align-items: center;
        padding-bottom: 1rem;
        --inputFontSize: 1rem;
    }

    div.compare-list :global(.selectContainer) {
        flex-grow: 1;
    }

    div.loader {
        display: flex;
        width: 100%;
        justify-content: center;
    }

    button {
        border-radius: 0.5rem;
        margin: 0px;
        height: 100%;
        margin-left: 0.5rem;
        padding: 0rem 1rem;
    }

    span.compiler-error {
        background-color: lightcoral;
        border-radius: 0.5rem;
        display: flex;
        justify-content: center;
        padding: 0.5rem;
        margin-bottom: 0.25rem;
    }

    table.debug-table td, table.debug-table th {
        border: 0.5px solid #cccccc;
        padding: 1px 2px;
    }

    table.debug-table {
        width: 100%;
        border: 0.5px solid #cccccc;
    }
</style>
