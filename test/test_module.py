from numpy import allclose, inf
from mesoscope import load, convert, downsample
from mesoscope.registrations import register
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

def test_reference_shape():
    data = fromtif('test/resources/output')
    ref = reference(data)
    assert ref.shape == (464, 576)

def test_downsample_shape():
    data = fromtif('test/resources/output')
    result = downsample(data, ds=2, dt=2)
    assert result.shape == (12, 232, 288)

def test_register_shape():
    data = fromtif('test/resources/output')
    registered, shifts =  register(data)
    assert registered.shape == (23, 464, 576)
    assert shifts.shape == (23, 2)
