from registration import CrossCorr
from numpy import meshgrid, linspace, dstack, asarray
from skimage.transform import PiecewiseAffineTransform, warp

def register(data):
    """
    Function for registering data. The reference image is computed as the mean of
    the provided data.

    Parameters
    ----------
    data : numpy array or images
        Raw image data as a numpy array or thunder images object.

    """

    if len(data.shape) == 4:
        algorithm = CrossCorr(axis=0)
    else:
        algorithm = CrossCorr()

    ref = data.mean().toarray()

    model = algorithm.fit(data, ref)
    registered = model.transform(data)
    shifts = model.toarray()

    return registered, shifts

def register_blocks_piecewise(data, size = (64, 64)):
    """
    Function for registering data. The reference image is computed as the mean of
    the provided data. The registration is done indpendently on blocks of specified
    size. The resulting shifts are used to compute a piecewise affine transform and shift
    the images

    Parameters
    ----------
    data : numpy array or images
        Raw image data as a numpy array or thunder images object.

    size : tuple
        Tuple specifying the block sizes to use for chuncking.
    """

    blocks = data.toblocks(chunk_size=size, padding=(int(size[0]*0.1),int(size[0]*0.1)))
    algorithm = CrossCorr()

    def reg_shifts(data):
        ref = data.mean(axis=0)
        model = algorithm.fit(data, ref)
        return model.toarray()

    shifts = blocks.map_generic(reg_shifts)

    src_cols = linspace(0, data.shape[1], shifts.shape[0]+1)
    src_cols = [x-src_cols[0]/2 for x in src_cols]
    src_cols = src_cols[:-1]
    src_rows = linspace(0, data.shape[2], shifts.shape[1]+1)
    src_rows = [x-src_rows[0]/2 for x in src_rows]
    src_rows = src_rows[:-1]
    src_rows, src_cols = meshgrid(src_rows, src_cols)
    src = dstack([src_cols.flat, src_rows.flat])[0]

    shifts = shifts.toarray().flatten()

    def piecewise_shift(item):
        (k, v) = item

        frame_shift = asarray([x[k] for x in shifts])
        dst = asarray([s + x for s, x in zip(src, frame_shift)])

        tform = PiecewiseAffineTransform()
        tform.estimate(src, dst)
        return warp(v, tform)

    return data.map(piecewise_shift, value_shape=data.value_shape, dtype=data.dtype, with_keys=True)

def register_blocks(data, size = (64, 64)):
    """
    Function for registering data. The reference image is computed as the mean of
    the provided data. The registration is done indpendently on blocks of specified
    size and shifts are also applied indpendently.

    Parameters
    ----------
    data : numpy array or images
        Raw image data as a numpy array or thunder images object.

    size : tuple
        Tuple specifying the block sizes to use for chuncking.
    """

    blocks = data.toblocks(chunk_size=size, padding=(int(size[0]*0.1),int(size[0]*0.1)))
    algorithm = CrossCorr()

    def reg(data):
        ref = data.mean(axis=0)
        model = algorithm.fit(data, ref)
        return model.transform(data).toarray()

    return blocks.map(reg).toimages()
