<script lang="ts">
    export let recs: string[];
</script>

{#if recs.length > 0}
{recs.some((rec) => {return rec.substring(0, 2) === '_*';}) ? '✔' : '✘'}
{#each recs as r, i}
    {#if (r[0] === '*')}
        *{r.substring(1)}{ recs.length - 1 === i ? '' : ', '}
    {:else if (r[0] === '_')}
        <b>{r.substring(1, r.length-1)}</b>{ recs.length - 1 === i ? '' : ', '}
    {:else if (r.substring(0, 3) === '≠ †')}
        ≠ †<span class="sourceipa">{r.substring(3)}</span>
    {:else}
        r{ recs.length - 1 === i ? '' : ', '}
    {/if}
{/each}
{/if}

<style>
    
</style>