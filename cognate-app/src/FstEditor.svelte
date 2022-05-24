<script lang="ts">
    export let fst: string;
    export let fstEditorWidth: number = 300;
    export let id: number;

    import {basicSetup} from "@codemirror/basic-setup"
    import {EditorState} from "@codemirror/state"
    import {EditorView, keymap} from "@codemirror/view"
    import {defaultKeymap} from "@codemirror/commands"
    import { onMount } from "svelte";

    const onUpdate = EditorView.updateListener.of((v) => {
        fst = v.state.doc.toString();
    });

    onMount(() => {

        let startState = EditorState.create({
            doc: fst,
            extensions: [basicSetup, keymap.of(defaultKeymap), onUpdate]
        })

        let view = new EditorView({
            state: startState,
            parent: document.getElementById(`editor-${id}`)
            
        }) 

        return () => {view.destroy()}
    })


    let initWidth = fstEditorWidth;
</script>

<div class="wrap" id="wrap">
    <div class="resizer" style="--initialWidth:{initWidth}px;" bind:clientWidth={fstEditorWidth}></div>
    <div class="resize-handle"></div>
    <div class="editor" id="editor-{id}"></div>
</div>

<style>
    div.wrap {
        width: fit-content;
        height: 100%;
        position: relative;
    }

    div.resizer {
        width: var(--initialWidth);
        height: 50%;
        resize: horizontal;
        overflow: hidden;
        opacity: 0;
        max-width: 50vw;
    }

    div.resize-handle {
        position: absolute;
        top: calc(50% - 25px);
        right: 0;
        width: 10px;
        height: 30px;
        border-radius: 0.25rem;
        background-color: black;
        z-index: -10;
        border: 2px solid lightgrey;
    }

    div.editor {
        border: 1px solid black;
        width: calc(100% - 10px);
        height: 100%;
        resize: none;
        position: absolute;
        top: 0;
        z-index: 10;
        overflow: auto;
    }
</style>