# Using CAPR

These are some basic instructions for interacting with the CAPR user interface. They are by no means exhaustive, and you may find that some things are unstable or require some more specific sequences of clicks to make sure they work well.

## Loading your data

If you are loading data for the first time, you will put it into the `data/` directory and should find that it is listed in the "available input sources" dropdown in the upper right corner of the screen. You may need to reload the page if you already have CAPR running. 

If you have an FST that should be generating boards (and it is properly configured, written, and in the `fsts/` directory), then simply click load and you should now have your boards visible. 

If you are starting from a blank FST (or one that generates no boards), loading the data while on the board page may throw an error (and freeze the page). Assuming you have not written an FST, it's best to follow the FST debug workflow below.

## FST debugging workflow

Starting a new FST? Trying to find out why a sound change isn't working like it should be? You can now use the FST editor to do basic FST debugging. 

Starting from a blank FST, open CAPR and switch to the FST editor. Select your data source and click load. The status at the top should show that loading completed, though likely nothing will appear anywhere else. Under the "select languages" dropdown, choose `Debug`. You should now see the doculects from your language displayed, with the `Apply Up` results and word/syllable columns displayed. Nothing is there, of course, as you have yet to write an FST.

To start writing and debugging a new FST, click the "Use new FST?" checkbox at the top and center of the screen. Now click the far left button "Switch FST" and the editor on the left side of the screen will be prepared for your new FST work. Start writing your new transducer, get a minimum sound change and end with the proper `save stack language.bin` format (see existing FSTs for examples), and then click "Go" on the right of the language dropdown. You should now see the word and output of applying the transducer upwards on each given word (or syllable).

Make sure to copy your FST or save/export it. Once you have a starting point, it is probably a good idea to just put it into the FST file in `fsts/` and then reload CAPR and start from there.

## Using the boards

Once you have an FST and want to start working on boards, you will unfortunately run into the fact that the current refishing code is quite broken, especially since CAPR was updated to be more language agnostic. See [#18](https://github.com/knightss27/capr/pull/18) for updates and progress on this front.