<script lang="ts">
    import FstEditor from "./FstEditor.svelte";
    import Select from "svelte-select";
    import type { CognateApp, FstComparison } from "./types";
    import initialTransducers from "./initialTransducers"
    import FstOutput from "./FstOutput.svelte";

    export let data: CognateApp;
    export let showNewFst = false;

    // Temporarily set our FSTs to existing options for testing.
    let oldFst = initialTransducers.oldTransducer;
	let newFst = initialTransducers.newTransducer;

    // Doculects to be selected from.
    // Should really be returned from server or something where they can be centrally defined.
    let doculects = [
        'Old_Burmese', 
        'Achang_Longchuan',
        'Xiandao',
        'Maru',
        'Bola',
        'Atsi',
        'Lashi'
    ]

    // Currently selected doculect list.
    let selectedDoculects = [];

    // TODO: move this to just replace call
    let rootUrl = "http://localhost:5000"

    // Calls the comparison route with our FSTs, returning the new data.
    const handleComparison = async () => {
        console.log('Calling comparison generator')

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
            console.log("Successfully compared FSTs");
            comparisonData = data;
        })
        .catch(e => {
            console.log(e)
        })
    }

    // Holds the data returned by the `compare-fst` route
    let comparisonData: FstComparison = null;
    // Lets us keep the editor widths the same when switching between new/old
	let fstEditorWidth = 300;
</script>


<main>
    <!-- Both of the FST editors, which are CodeMirror 6 instances -->
    <div class="editor">
        {#if showNewFst}
        <FstEditor bind:fst={newFst} id={1} bind:fstEditorWidth {oldFst} />
        {:else}
        <FstEditor bind:fst={oldFst} id={2} bind:fstEditorWidth {oldFst} />
        {/if}
    </div>
    <!-- The compare list, which is a massive table with a Select at the top -->
    <div class="compare">
        <div class="compare-list">
            <!-- Select component from @svelte-select -->
            <Select items={doculects} isMulti={true} bind:value={selectedDoculects} />
            <button on:click={handleComparison}>Go</button>
        </div>
        {#if comparisonData}
            <FstOutput data={comparisonData} langsUnderStudy={selectedDoculects.map(p => p.value)} />
        {/if}
    </div>
</main>

<style>
    main {
        width: 100%;
        height: calc(100% - 62px);
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
    }

    div.compare-list :global(.selectContainer) {
        flex-grow: 1;
    }

    button {
        border-radius: 0.5rem;
        margin: 0px;
        height: 100%;
        margin-left: 0.5rem;
        padding: 0rem 1rem;
    }
</style>
