# mesoscope

[![Latest Version](https://img.shields.io/pypi/v/mesoscope.svg?style=flat-square)](https://pypi.python.org/pypi/mesoscope)
[![Build Status](https://img.shields.io/travis/sofroniewn/mesoscope/master.svg?style=flat-square)](https://travis-ci.org/sofroniewn/mesoscope)
[![Binder](https://img.shields.io/badge/launch-binder-red.svg?style=flat-square)](http://mybinder.org:/repo/sofroniewn/mesoscope)


> preprocessing and conversion for mesoscope data

This package contains a module and command line tool to process raw data from the [two-photon random access mesoscope](https://elifesciences.org/content/5/e14472) (2P-RAM). The raw output of the mesocope, via the ScanImage control software, is a matrix of resonant scan lines across multiple rois stored as TIF files. For the majority of applications, users will want to merge and reshape their contents into images that are appropriately merged and reshaped. This module helps you do that.

# install

You can install using pip

```
pip install mesoscope
```

# example

Here we'll convert the example test data included with the repository

```python
import mesoscope as ms

data, meta = ms.load('test/resources/input')
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

This will create a folder `output` with the converted images. Type `mesoscope convert -h` to see other options. Note that during image writing `int16` values will be written as `uint16` so any negative values will be clipped at 0.

```
mesoscope summarize input/ output/
```

This will create a folder `output` with the summary images and movies. Type `mesoscope summarize -h` to see other options. Using the `--mean` flag will generate a mean image. Using the `--localcorr` option a local correlation image will be computed. The neighborhood of the local correlation can be set with the `--size` option. Using the `--movie` option will generate a movie. The movie can be downsampled in space with `--ds` and time with `--dt`. If metadata is present then it will be used to generate length scales and timestamps for the movie. If the data recorded is a volume than one movie will be generated for each plane, and the local correlation and spatial downsampling will be done independently on each plane.

```
mesoscope register input/ output/
```

This will create a folder `output` with the registered images and shifts. Type `mesoscope register -h` to see other options. The registration will first compute a reference image by taking a mean of all the data. It will then perform a global cross correlation based rigid transform of the data to align each frame to this reference. If the data is a volume each z-plane will be treated independently. A `.csv` file containing the shifts will also be saved.

```
mesoscope regions input.json
```

This will create a file `image-input.tif` showing the regions. Type `mesoscope regions -h` to see other options. If given a 2d image `--image` the regions will be overlayed onto it. If given another set of regions `--compare` and a `--threshold` then the `precision`, `recall`, and `inclusion`, `exclusion` scores will be calculated and saved. The hits (green) and misses (red) will also be plotted saved as an image.

For all commands, the option `--master spark://xxxxx:7077` allows you to specify a Spark cluster master node by providing the URL of the master node. When using this option, any paths to input and output folders should be given with full path names.

# use as a module

The `mesoscope` package includes the following methods

#### `data, meta = load(path, metapath=None, engine=None)`

Loads both data and metadata from the specified `path`. The optional `metapath` allows a seperate path for the metadata. If not given the metadata will be looked for inside `path`. The optional `engine` can be used to load the data using a parallel backend. Currently supports either `None` (for local compute) or a `SparkContext` (for parallelization using a Spark cluster).

#### `newdata, newmeta = convert(data, meta)`

Converts the given data using the provided metadata. The `data` should be a `numpy` array or a `thunder` `images` object.

#### `newdata = downsample(data, ds=None, dt=None)`

Downsamples data in space with `ds` and time with `dt`. `ds` should be either an `int` or a `tuple`. `dt` should be an `int`.

#### `registered, shifts = register(data)`

Computes rigid cross correlation based registration of `data` to `ref`. If `data` is volumetric z-planes are treated independently.
