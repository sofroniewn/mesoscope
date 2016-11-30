from numpy import percentile

def norm(image, min_percentile=0, max_percentile=100):
    """
    Clip and rescale an image to be between [0, 1]
    Parameters
    ----------
    image : a 2d image
        The image to be rescaled.
    min : float
        Lower percentile value.
    max : float
        Upper percentile value.
    """

    tmp = image.astype('float').clip(percentile(image,min_percentile),percentile(image,max_percentile))
    tmp = tmp - tmp.min()
    return tmp/tmp.max()
