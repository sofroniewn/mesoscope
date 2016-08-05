from numpy import allclose, inf
from mesoscope import load, convert
from thunder.images import fromtif

def test_load_meta():
    data, meta = load('test/resources/input')
    assert meta['nrois'] == 9
    assert len(meta['rois']) == 9
    assert meta['nplanes'] == 1
    assert meta['nchannels'] == 1
    assert meta['shape'] == (23, 5152, 64)

def test_load_data():
    data, meta = load('test/resources/input')
    assert data.shape == (23, 5152, 64)

def test_convert_meta():
    data, meta = load('test/resources/input')
    newdata, newmeta = convert(data, meta)
    assert newmeta['nrois'] == 1
    assert len(newmeta['rois']) == 1
    assert newmeta['nplanes'] == 1
    assert newmeta['nchannels'] == 1
    assert newmeta['shape'] == (23, 464, 576)

def test_convert_data():
    data, meta = load('test/resources/input')
    newdata, newmeta = convert(data, meta)
    assert newdata.shape == (23, 464, 576)
    assert newdata.dtype == 'int16'

def test_convert_data_array():
    data, meta = load('test/resources/input')
    newdata, newmeta = convert(data.toarray(), meta)
    assert newdata.shape == (23, 464, 576)

def test_convert_ground_truth():
    data, meta = load('test/resources/input')
    newdata, newmeta = convert(data, meta)
    truth = fromtif('test/resources/output')
    assert newdata.shape == truth.shape
    assert allclose(newdata.clip(0, inf), truth)
