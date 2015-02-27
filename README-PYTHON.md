ACES 1.0.0
==========

Informations about ACES
-----------------------

The **ACES** project home page is here: http://www.oscars.org/aces

Python Utilities
----------------

This bundle contains reference implementations of the Academy / ASC Common LUT Format (CLF) and the ACES Clip Metadata formats. 

Documentation on the formats can be found here: https://github.com/ampas/aces-dev/tree/master/documents

The Python implementations:

- Include reading, writing and querying data structures
	- And processing data where appropriate
- Are meant to be open, accessible, easily understood
- Are not meant to be fast
	- Each really needs a C/C++ implementation

CLF
--- 
### Library
clf.py

- Provides simple Python interface to read, write and query CLFs, and process colors with CLFs
- Implements the S-2014-006 specification included in the ACES 1.0 release
- Implements the Autodesk CTF extensions
	- Documented here: http://docs.autodesk.com/flamepremium2015/index.html?url=files/GUID-460BA05D-3AB7-4BE2-AD30-01F9D3440CD8.htm,topicNumber=d30e147706
	- Some extensions have proprietary behavior which is not open.
		- Ex. The Reference ProcessNode
- Does little checking for validity of the ProcessList data
- Includes examples of
	- Creating a ProcessList and various ProcessNodes
	- Reading a CLF
	- Writing a CLF
	- Processing colors with a CLF 

### Tools
clfinfo.py

- Prints information about a CLF to the terminal

filterImageWithCLF.py

- Reads an image, applies a CLF to the image, writes a new image 

convertLUTtoCLF.py

- Converts from the different LUT formats to CLF
- LUT formats currently supported are: spi1d, spi3d and csp

convertCLFtoLUT.py

- Converts from CLF to different LUT formats
- LUT formats currently supported are: spi1d, spi3d, csp, clf

convertOCIOtoCLF.py

- Converts from a set of OCIO colorspace definitions to CLF
- Accepts source color spaces and destination color spaces.
- Currently supported OCIO transforms: Group, File, Log and Matrix
	- Missing transforms: Allocation, CDL, Exponent
		- ColorSpace, Display and Look transforms not supported either. These are references to other transforms so should be simple to support eventually.
	- Not all flags are supported.
		- Ex. 'inverse' for Matrix Transforms

Clip Metadata
-------------
### Library
clip.py

- Provides simple Python interface to read, write and query Clip Metadata.
- Implements the TB-2014-009 specification included in the ACES 1.0 release
- Includes examples of
	- Creating ClipMetadata and various sub-components
	- Reading a Clip Metadata file
	- Writing a Clip Metadata file
- Does little checking for validity of the data
- No support for formatting dates, uuids or other data stored in fields

### Tools
clipinfo.py

- Prints information about a Clip to the terminal

Would be nice to have
---------------------
### CLF

- A Group ProcessNode that can group lists of other process nodes
	- Useful for organizing list of nodes that represent a filter/transform generated elsewhere
- An 'inverse' style for LUT1D
- Official acceptance of Autodesk extensions
	- Gamma
	- Log
	- Reference
		- With some separation of Autodesk-specific functionality like the 'alias' attribute
	- 'bypass' flag
- These Autodesk extensions seem less general, but still useful to them:
	- DynamicParameter
	- ExposureContrast

### Clip

- Example integration of Clip support into application
- Questions to answer about how file should work in a multi-user scenario


Thanks
------
These scripts and modules were the product of work and conversations with a number of people. Thanks go to:

- Jim Houston
- Thomas Mansencal
- Doug Walker

Dependencies
------------
The *Python* package depends on the following libraries:

- **OpenImageIO**: http://openimageio.org
- **OpenColorIO**: http://opencolorio.org/
