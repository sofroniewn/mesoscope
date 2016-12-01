from numpy import maximum, percentile, full, nan, where, tile, inf, isnan
from skimage.measure import regionprops
from neurofinder import match, centers, shapes
from regional import many
from extraction.model import ExtractionModel
from .utils import norm
from .CC import CC

def compare(model, modelReference, threshold):
    """
    Compare two extraction models.

    Parameters
    ----------
    model : ExtractionModel
        Model for comparision.

    modelReferrence : ExtractionModel
        Reference model to be compared to, can be ground truth.

    threshold : float
        Distance threshold for matching sources.
    """

    recall, precision = centers(modelReference.regions, model.regions, threshold)
    inclusion, exclusion = shapes(modelReference.regions, model.regions, threshold)
    if recall == 0 and precision == 0:
        combined = 0
    else:
        combined = 2 * (recall * precision) / (recall + precision)
    count = model.regions.count
    return {'count': count,
            'combined': combined,
            'recall':recall,
            'precision':precision,
            'inclusion':inclusion,
            'exclusion':exclusion,
            'threshold':threshold}

def overlay(regions, image=None, compare=None, threshold=inf, correct=False):
    """
    Overlay regions onto reference image, with optional comparison regions.

    Parameters
    ----------
    regions : many regions
        Regions from regional package to be visualized.

    image : array-like, optional, default = None
         Base image, can provide a 2d array,
         if unspecified will be black.

    compare : many regions, default = None
        Regions to be compared to if provided.

    threshold : float, default = inf
        Distance threshold for matching sources.

    correct : bool, default = False
        If True and a comparision given will only show correct regions
    """

    if image is not None:
        if image.max() > 1:
            im = norm(image)
        else:
            im = image
        size = im.shape
    else:
        size = (max([r.bbox[2] for r in regions])+1, max([r.bbox[3] for r in regions])+1)
        if compare is not None:
            sizeCompare = (max([r.bbox[2] for r in compare])+1, max([r.bbox[3] for r in compare])+1)
            size = (maximum(size[0], sizeCompare[0]), maximum(size[1], sizeCompare[1]))
        im = full(size, 0.0)


    if compare is not None:
        matches = match(regions, compare, threshold)
        matchesCompare = full(compare.count,nan)

        for ii in where(~isnan(matches))[0]:
            matchesCompare[matches[ii]] = ii

        if any(~isnan(matches)):
            hits = many([regions[i] for i in where(~isnan(matches))[0]])
            h = hits.mask(size, background='black', fill=None, stroke=[0, 0.7, 0])
        else:
            h = full((size[0], size[1], 3), 0.0)
        if any(isnan(matches)):
            falseAlarms = many([regions[i] for i in where(isnan(matches))[0]])
            fA = falseAlarms.mask(size, background='black', fill=None, stroke=[0.7, 0, 0])
        else:
            fA = full((size[0], size[1], 3), 0.0)
        if any(~isnan(matchesCompare)):
            truePositives = many([compare[i] for i in where(~isnan(matchesCompare))[0]])
            tP = truePositives.mask(size, background='black', fill=None, stroke=[0, 0, 0.7])
        else:
            tP = full((size[0], size[1], 3), 0.0)
        if any(isnan(matchesCompare)):
            misses = many([compare[i] for i in where(isnan(matchesCompare))[0]])
            m = misses.mask(size, background='black', fill=None, stroke=[0.7, 0.7, 0])
        else:
            m = full((size[0], size[1], 3), 0.0)
        if correct:
            mask = maximum(tP, h)
        else:
            mask = maximum(maximum(maximum(tP, fA), h), m)
    else:
        mask = regions.mask(size, background='black', fill=None, stroke=[0, 0.7, 0])


    base = tile(im,(3,1,1)).transpose(1,2,0)
    return maximum(base, mask)

def filter_shape(model, min_diameter=7, max_diameter=13, min_eccentricity=0.2):
    """
    Filter extraction model regions based on shape criterion.

    Parameters
    ----------
    model : ExtractionModel.

    min_diameter : float, default 7.
        Minimum allowed diameter of regions

    max_diameter : float, default 13.
        Maxium allowed diameter of regions

    min_eccentricity : float, default 0.2.
        Minimum allowed eccentricity of regions
    """

    regions = []
    for region in model.regions:
        mask = region.mask(fill=[1, 1, 1], background=[0, 0, 0])[:,:,0]
        props = regionprops(mask.astype('int'))[0]
        if (props.eccentricity > min_eccentricity) and (props.equivalent_diameter > min_diameter) and (props.equivalent_diameter < max_diameter):
            regions.append(region)
    return ExtractionModel(regions)
