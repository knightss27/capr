<script>
	import { onMount, getContext } from 'svelte';
	// import { key } from './menu.js';
	
	export let isDisabled = false;
	export let text = '';
	
	import { createEventDispatcher } from 'svelte';
	const dispatch = createEventDispatcher();	
	
	const { dispatchClick } = getContext(1);
	
	const handleClick = e => {
		if (isDisabled) return;
		
		dispatch('click');
		dispatchClick();
	}
</script>

<style>
	div {
		padding: 4px 15px;
		cursor: default;
		font-size: 14px;
		display: flex;
		align-items: center;
		grid-gap: 5px;
        border-radius: 0.5rem;
	}
	div:hover {
		background: #0002;
	}
	div.disabled {
		color: #0006;
	}
	div.disabled:hover {
		background: white;
	}
</style>

<div 
  class:disabled={isDisabled}
  on:click={handleClick}
>
	{#if text}
		{text}
	{:else}
		<slot />
	{/if}
</div>
