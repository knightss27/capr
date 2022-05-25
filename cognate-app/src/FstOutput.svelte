<script lang="ts">
    import FstReconstruction from "./FstReconstruction.svelte";
    import type { FstComparison } from "./types";

    export let data: FstComparison;
    export let langsUnderStudy: string[];

    let chapterTitles = {i:'Initials', m:'Medials', r:'Rimes', t:'Tones'};

    const getBg = (status: string) => {
        if (status === "smiling") {
            return "lightgreen"
        } else if (status === "frowning") {
            return "lightcoral"
        } else {
            return "white"
        }
    }

    console.log(data);
</script>

<div>
    {#each Object.keys(data.chapters) as chapterId}
        <h1>{chapterTitles[chapterId]}</h1>
        {#each data.chapters[chapterId] as section}
            <h2>{section.title}</h2>
            <table>
                <tr>
                    <th>Gloss</th>
                    {#each langsUnderStudy as lang}
                        <th>{lang}</th>
                    {/each}
                </tr>
                {#each section.rows as row}
                <tr style="background-color:{getBg(row.status)};">
                    <td>{row.gloss ? `"${row.gloss}"` : ""}</td>
                    {#each row.ipas as ipa}
                    <td class="sourceipa"><b>{ipa}</b></td>
                    {/each}
                </tr>
                <tr style="background-color:{getBg(row.status)};">
                    <td>{row.old_reconstruction ? row.old_reconstruction : ""}</td>
                    {#each row.old_reconstructions as recs}
                        <td>
                            <FstReconstruction recs={recs.split(", ")} />
                        </td>
                    {/each}
                </tr>
                <tr class="last" style="background-color:{getBg(row.status)};">
                    <td>{row.new_reconstruction ? row.new_reconstruction : ""}</td>
                    {#each row.new_reconstructions as recs}
                        <td>
                            <FstReconstruction recs={recs.split(", ")} />
                        </td>
                    {/each}
                    <td>
                        {(row.status == "smiling") ? '😊' : (row.status == "frowning") ? '🙁' : ''}
                    </td>
                </tr>
                {/each}
            </table>
        {/each}
    {/each}
</div>


<style>
    table {
        border-collapse: collapse;
        width: 100%;
    }

    table, th {
        border: solid black;
        border-width: 1px 0 1px 0;
    }

    tr.last > td {
        padding-bottom: 1em;
    }

    td {
        text-align: center;
    }
</style>