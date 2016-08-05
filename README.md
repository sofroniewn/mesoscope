# mesocope

[![Latest Version](https://img.shields.io/pypi/v/meoscope.svg?style=flat-square)](https://pypi.python.org/pypi/mesoscope)
[![Binder](https://img.shields.io/badge/launch-binder-red.svg?style=flat-square)](http://mybinder.org:/repo/sofroniewn/mesoscope)

> preprocessing and conversion for mesoscope data

This package contains a module and command line tool to process raw data from the [two-photon random access mesoscope](https://elifesciences.org/content/5/e14472) (2P-RAM). The raw output of the mesocope, via the ScanImage control software, is a matrix of resonant scan lines across multiple rois stored as TIF files. For the majority of applications, users will want to merge and reshape their contents into images that are appropriately merged and reshaped. This module helps you do that.

# install

You can install using pip

```
pip install mesoscope
```

# example

```python
import mesoscope as ms

data, meta = ms.load('test/resources')
newdata, newmeta = ms.convert(data, meta)

data.shape
>> (23, 5152, 64)

converted.shape
>> (23, 464, 576)
```

# use as command line tool

Given a directory with input TIF files and a metadata file as JSON, just call

```
mesoscope convert input/ output/
```

This will create a folder `output` with the converted images. Type `mesoscope convert -h` to see other options.

# use as a module

The `mesocope` package includes just two methods

#### `data, meta = load(path, engine=None)`

Loads both data and metadata from the specified `path`. The optional `engine` can be used to load the data using a parallel backend. Currently supports either `None` (for local compute) or a `SparkContext` (for parallelization using a Spark cluster).

#### `newdata, newmeta = convert(data, meta)`

Converts the given data using the provided metadata. The `data` should be a `numpy` array or a `thunder` `images` object.
