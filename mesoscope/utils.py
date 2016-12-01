from numpy import percentile, arange, polyfit, polyval

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

def detrend(y, order=5):
        """
        Detrend series data with linear or nonlinear detrending.
        Preserve intercept so that subsequent operations can adjust the baseline.
        Parameters
        ----------
        order : int, optional, default = 5
            Order of polynomial, for non-linear detrending only
        """

        x = arange(len(y))
        p = polyfit(x, y, order)
        p[-1] = 0
        yy = polyval(p, x)
        return y - yy
