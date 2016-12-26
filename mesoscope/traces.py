from numpy import zeros, subtract
from extraction.model import ExtractionModel

def neuropilModel(model, inner=3, outer=8, mask=True, shape=(512, 512)):
    regionsNeuropil = model.regions.outline(inner, outer)
    regionsNeuropil = regionsNeuropil.crop(zeros(len(shape)), shape)
    if mask:
        mask = model.regions.mask(fill=[1, 1, 1], base=zeros(shape))[:,:,0]
        regionsNeuropil = regionsNeuropil.exclude(mask)
    return ExtractionModel(regionsNeuropil)

def dff(data, model, neuropil=True, inner=3, outer=8):
    t = model.transform(data).normalize()
    if neuropil:
        modelNeuropil = neuropilModel(model, inner=inner, outer=outer, shape=data.shape[1:])
        tN = modelNeuropil.transform(data).normalize()
        t = t.element_wise(tN, subtract)
    return t
