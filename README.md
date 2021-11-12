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

### v1.1.0
* Modularised code
* Added configuration file
* Added user input
* Updated textures to 1.17.1
* Added argument parsing
* Error catching for invalid directory or reference PNG name

### v1.2.0
* Improved algorithm speed
* Added whitelist and blacklist files

## TODO
* GUI