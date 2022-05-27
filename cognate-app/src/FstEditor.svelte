<script lang="ts">
    export let fst: string;
    export let fstEditorWidth: number = 300;
    export let id: number;
    export let oldFst: string = "";

    import {basicSetup} from "@codemirror/basic-setup"
    import {EditorState, Extension, Facet, RangeSetBuilder} from "@codemirror/state"
    import {Decoration, DecorationSet, EditorView, keymap, ViewPlugin, ViewUpdate} from "@codemirror/view"
    import {defaultKeymap} from "@codemirror/commands"
    import { onMount } from "svelte";
    import * as Diff from "diff";

    // Diff calculation for displaying changes
    let changedRanges: Diff.Hunk[] = [];
    const calcDiff = (): Diff.Hunk[] => {
        let diff = Diff.structuredPatch('OLD FST', 'NEW FST', oldFst, fst, '', '', {context: 0});
        return diff.hunks
    }

    // Colors for displaying the diffs as line highlights
    const baseTheme = EditorView.baseTheme({
        "&light .cm-code-addition": {backgroundColor: "#90ee903d"},
        "&light .cm-code-removal": {backgroundColor: "#f080803d"},
        ".cm-selectionMatch": {backgroundColor: "lightblue !important"},
        ".cm-code-fst-header": {color: "red"}
    })

    // A bunch of CodeMirror specific stuff for highlighting diff regions.
    // It works so I'm using it, though it is definitely not the cleanest solution.
    const colorLine = (type: boolean): Decoration => {
        return Decoration.line({
            attributes: {class: `cm-code-${type ? 'addition' : 'removal'}`}
        })
    } 
    function stripeDeco(view: EditorView) {
        let builder = new RangeSetBuilder<Decoration>()
        if (id != 1) {
            return builder.finish();
        }

        changedRanges = calcDiff();
        for (let {from, to} of view.visibleRanges) {
            for (let pos = from; pos <= to; pos++) {
                let line = view.state.doc.lineAt(pos);

                // Some optional highlighting for common '###' format for differentiating FST sections.
                if (line.text.lastIndexOf("#") == line.text.length-1) {
                    builder.add(line.from, line.from, Decoration.line({attributes: {class: 'cm-code-fst-header'}}))
                }

                for (let r of changedRanges) {
                    if (line.number >= r.newStart && line.number < r.newStart+r.newLines) {
                        builder.add(line.from, line.from, colorLine(r.newLines >= r.oldLines));
                    }
                }
            }
        }
        return builder.finish()
    }
    const showStripes = ViewPlugin.fromClass(class {
        decorations: DecorationSet

        constructor(view: EditorView) {
            this.decorations = stripeDeco(view)
        }

        update(update: ViewUpdate) {
            if (update.docChanged || update.viewportChanged) {
                fst = update.state.doc.toString();
                // Don't do highlighting if we are the old FST
                if (id == 1) {
                    this.decorations = stripeDeco(update.view)
                }
            }
        }
        }, {
        decorations: v => v.decorations
    })
    const diffHighlight = (): Extension => {  
        return [
            baseTheme,
            showStripes
        ]
    }

    // When the component loads, we create the CodeMirror component,
    // destroying it once the component is unloaded.
    onMount(() => {

        let startState = EditorState.create({
            doc: fst,
            extensions: [basicSetup, keymap.of(defaultKeymap), diffHighlight()]
        })

        let view = new EditorView({
            state: startState,
            parent: document.getElementById(`editor-${id}`)
        }) 

        return () => {view.destroy()}
    })

    // Temp. variable to let us not update our width too many times.
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