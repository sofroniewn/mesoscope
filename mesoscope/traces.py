from numpy import zeros, subtract
from extraction.model import ExtractionModel

def neuropilModel(model, inner=3, outer=8, mask=True):
    regionsNeuropil = model.regions.outline(inner, outer)
    if mask:
        mask = model.regions.mask(fill=[1, 1, 1], base=zeros(mean.shape))[:,:,0]
        regionsNeuropil = regionsNeuropil.exclude(mask)
    return ExtractionModel(regionsNeuropil)

def dff(data, model, neuropil=True, inner=3, outer=8):
    t = model.transform(data).normalize()
    if neuropil:
        modelNeuropil = neuropilModel(model, inner=inner, outer=outer)
        tN = modelNeuropil.transform(data).normalize()
        t = t.element_wise(tN, subtract)
    return t
