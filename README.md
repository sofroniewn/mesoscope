# mesocope

> preprocessing and conversion for mesoscope data

This package contains a module and command line tool to process raw data from the [twp-photon random access mesoscope](https://elifesciences.org/content/5/e14472) (2P-RAM). The raw output of the mesocope, via the ScanImage control software, is a matrix of resonant scan lines stored as TIF files. For the majority of applications, users will want to convert from this format into TIF files with 2D or 3D images that are appropriately merged and reshaped. 

# install

You can install using pip

```
pip install mesoscope
```

# example

```python
import mesoscope as ms

data, metadata = ms.load('test/resources')
converted = ms.convert(data, metadata)
```

# use as command line tool

Given a directory with input TIF files and a metadata file as JSON, just call

```
mesoscope convert input/ output/
```

This will create a folder `output` with the converted images.

# use as a module

The `mesocope` package includes just two methods

#### `load(path, engine=None)`

Loads both data and metadata from the specified `path`. The optional `engine` can be used to load the data using a parallel backend.

#### `convert(data, metadata)`

Converts the given data using the provided metadata. The `data` should be a `numpy` array or a `thunder` `images` object.