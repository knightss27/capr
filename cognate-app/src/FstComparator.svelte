<script lang="ts">
    import FstEditor from "./FstEditor.svelte";
    import Select from "svelte-select";
    import type { CognateApp, FstComparison } from "./types";
    import initialTransducers from "./initialTransducers"
    import FstOutput from "./FstOutput.svelte";

    export let data: CognateApp;

    let oldFst = initialTransducers.oldTransducer;
	let newFst = initialTransducers.newTransducer;


    let doculects = [
        'Old_Burmese', 
        'Achang_Longchuan',
        'Xiandao',
        'Maru',
        'Bola',
        'Atsi',
        'Lashi'
    ]

    let selectedDoculects = [];

    // TODO: move this to just replace call
    let rootUrl = "http://localhost:5000"
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

    let comparisonData: FstComparison = null;
</script>


<main>
    <div class="editor">
        <FstEditor bind:fst={oldFst} id={1} />
        <FstEditor bind:fst={newFst} id={2} />
    </div>
    <div class="compare">
        <div class="compare-list">
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
        height: 100%;
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
    }
</style>
