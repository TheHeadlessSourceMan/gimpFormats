# gimpFormats
A pure python implementation of the GIMP xcf image format.

This was created primarily to serve as a file conversion tool for my smartimage library (coming soon).  The idea is you can "upgrade" from a GIMP document to a smartimage.

That being said, it should be generally useful to those who want to fiddle with GIMP files using Python.

Currently supports:

    * Loading xcf files (up to current GIMP version 2.10)
    * Getting image hierarchy and info
    * Getting image for each layer (PIL image)


Currently not supporting:

    * Saving
    * Programatically alter documents (add layer, etc)
    * Rendering a final, compositied image

The home for this project is on my website, here:
https://theheadlesssourceman.wordpress.com/2019/05/10/gimpformats/

