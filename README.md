# Common_Birkbeck_TaskEngine
Scripts that can be used across the Birkbeck/TaskEngine ecosystem.

## Reporting functions
These are scripts useful in reporting (usually visual) data

### createPresentation.m
Used to create a presentation object, which can then be passed to addImgToPresentation when adding images to the presentation

## Video functions
These are scripts that can be used on video data.

### autoSyncScreenflash.py
Presents a couple methods to find specific points in screenflow video data. Specifically has a pipeline to find the offset of the screenflash (D115/DIN115), but also presents a use case to find any image that would be repeatable in other videos.

### splitMOVByFrame.py
Simple script that takes in either a single file or a folder of files (mp4) and splits them to their respective frames.
