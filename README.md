# gimpFormats
A pure python implementation of the GIMP xcf image format.

This was created primarily to serve as a file conversion tool for my smartimage library (coming soon).  The idea is you can "upgrade" from a GIMP document to a smartimage.

That being said, it should be generally useful to those who want to fiddle with GIMP files using Python.

Currently supports:

    * Loading xcf files (up to current GIMP version 2.10)
    * Getting image hierarchy and info
    * Getting image for each layer (PIL image)
	* .gbr brushes
	* .vbr brushes
	* .gpl palette files
	* .pat pattern files

Currently testing/unstable:

    * Saving
    * Programatically alter documents (add layer, etc)
	* gimp .gtp tool preset files - scheme file format is difficult to parse
	* .ggr gradients - reads/saves fine, but I need to come up with a way to get the actual colors
	* .gih brush sets - BUG: seems to have more image data per brush than what's expected
	* .gpb brush - should work, but I need some test files

Currently not implemented:	

    * Rendering a final, compositied image
	* Exported paths in .svg format. - Reading should be easy enough, but I need to ensure I don't get a full-blown svg in the mix
	* Standard "parasites"

The home for this project is on my website, here:
https://theheadlesssourceman.wordpress.com/2019/05/10/gimpformats/

