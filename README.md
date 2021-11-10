# PNG to MC Blocks Converter
## Overview
This is a Python3 script that converts a PNG to Minecraft Blocks that match the texture the best. I made this program out of my need to recreate a PNG in Minecraft.

## Dependencies
* Python3 (tested with v3.9.7)
* Pillow 6.2.1 (`pip install pillow`)

## Debugging
This program has been tested on the above mentioned dependencies, without any issues. If you run into any errors please make sure you are on this version because it is known to work. If you still are having issues on the aforementioned version, just send me a message on my [GitHub](https://github.com/mattdocherty314)

## Program Use
To change the blocks or the .png selected available you will need to change it in the code and supply the resources. Note: It will find the closest texture based on average pixel value.

## Version History
### v1.0.0
* Finished base version

## TODO
* Configuration settings
* Argument parsing
* Read valid texture list from file
* Better code comments
* Error catching
* Use of multiprocessing
* Good enough search (take a threshold and first N that meet it)
* GUI