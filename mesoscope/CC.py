from numpy import corrcoef, concatenate, tile, array, isnan, pad, where
from scipy.ndimage.filters import gaussian_filter
from thunder.images.readers import fromarray, fromrdd
from skimage.feature import blob_log
from skimage.exposure import equalize_adapthist
from single_cell_detect import watershed_edge as detect
from extraction.model import ExtractionModel
from .utils import norm

class CC(object):
    """
    Source extraction using central correlations on the local correlation.
    """
    def __init__(self, diameter=10, clip_limit=0.04, theshold=0.2, sigma_blur=0, boundary=(0,0)):
        self.diameter = diameter
        self.clip_limit = clip_limit
        self.theshold = theshold
        self.sigma_blur = sigma_blur
        self.boundary = boundary

    def fit(self, images):
        # compute local correlation of each pixel after bluring a cell bodies worth
        localcorr = images.localcorr(self.diameter)

        # detect blobs in local correlations corresponding to size of a cell
        centers = findcenters(localcorr[:,self.boundary[0]:-self.boundary[1]], diameter = self.diameter, clip_limit=self.clip_limit, threshold = self.theshold)
        centers = array([[x[0], x[1]+self.boundary[0]] for x in centers])

        # reshape the data into blocks around each center coordinate
        reshaped = images.map(lambda x: selectCenters(x, centers, self.diameter))

        # compute cross correlation with central pixels timeseries in each block
        stack = centercorr(reshaped, sigma_blur=self.sigma_blur)

        # detect boundaries of each putative cell and reshift coordinates back to original image
        masks = [detect(img, dilationSize=2, radial=True, filterSize=int(5*self.diameter)) for img in stack]
        regions = [mask_to_coords(masks[ii], centers[ii]) for ii in range(len(centers))]

        return ExtractionModel(regions)

def selectCenters(image, centers, size):
    size = int(size)
    padded = pad(image, size, 'constant')
    return array([padded[center[0]:center[0]+2*size+1,center[1]:center[1]+2*size+1] for center in centers])

def mask_to_coords(mask, center):
    coordinates = where(mask)
    return [[coordinates[0][ii] + center[0] - int(mask.shape[0]/2), coordinates[1][ii] + center[1] - int(mask.shape[1]/2)] for ii in range(len(coordinates[0]))]

def centercorr(self, sigma_blur=0):
    """
    Correlate every pixel in an block to its central pixel, possible
    with blurring that pixel before hand.

    Parameters
    ----------
    size : int or tuple, optional, default = 0
        Size of the filter in pixels. If a scalar, will use the same filter size
        along each dimension.
    """

    nimages = self.shape[0]

    # spatially average the original image set over the specified neighborhood
    def restrictedGaussianFilter(x, sigma):
        return array([gaussian_filter(y, sigma) for y in x])

    if sigma_blur > 0:
        blurred = self.map(lambda x: restrictedGaussianFilter(x, sigma_blur))
    else:
        blurred = self

    def copyCenter(x):
        return tile(x[:, x.shape[1]/2+1, x.shape[2]/2+1], (x.shape[1], x.shape[2], 1)).transpose(2,0,1)

    blurred = blurred.map(copyCenter)

    # union the averaged images with the originals to create an
    # Images object containing 2N images (where N is the original number of images),
    # ordered such that the first N images are the central ones.
    if self.mode == 'spark':
        combined = self.values.concatenate(blurred.values)
        combined_images = fromrdd(combined.tordd())
    else:
        combined = concatenate((self.values, blurred.values), axis=0)
        combined_images = fromarray(combined)

    # correlate the first N (central) records with the last N (original) records
    series = combined_images.toseries()
    corr = series.map(lambda x: corrcoef(x[:nimages], x[nimages:])[0, 1]).toarray()
    corr[isnan(corr)] = 0

    def centerFilter(img):
        x = img.shape[0]/2+1
        y = img.shape[1]/2+1
        img[x,y] = (img[x+1,y] + img[x-1,y] + img[x,y+1] + img[x,y-1])/4
        return img

    corr = array([centerFilter(im) for im in corr])

    return corr

def findcenters(image, diameter = 10, clip_limit=0.04, threshold = 0.2):
    """
    Find centers based on local correlation image

    Parameters
    ----------
    image : thunder images data.

    diamter : float, default 10.
        Expected diameter of cells

    clip_limit : float, default 0.04.
        Clip limit of adaptive histogram equalization

    thershold : float, default 0.2.
        Threshold for blob detection. Decreasing the threshold will detect more blobs
    """
    def close_divsor(n, m):
        n = int(n)
        m = int(m)
        if m > n:
            return n
        while n % m:
            m += 1
        return m

    image = norm(image)
    kernel_size = (close_divsor(image.shape[0], 2*diameter), close_divsor(image.shape[1], 2*diameter))
    image = equalize_adapthist(image, kernel_size=kernel_size, clip_limit=clip_limit)
    image = norm(image)
    coords = blob_log(image, min_sigma=diameter/2.335, max_sigma=diameter/2.335*2, num_sigma=10, threshold=threshold)
    return array([x[:2].astype(int) for x in coords if x[0] > diameter/2 and x[1] > diameter/2 and image.shape[0] - x[0] > diameter/2 and image.shape[1] - x[1] > diameter/2])
