import thunder
from numpy import array, concatenate, multiply, argsort
from os.path import join, exists
from os import mkdir, makedirs
import json
from glob import glob

def loadImages(path, engine=None):
    #Load metadata, tiff stacks, and reshape
    meta = loadMeta(path + '.json')
    if meta['merge']:
        order = meta['order']
    else:
        order = False
    data = loadTiff(path + '.tif', meta['nplanes'], meta['nrois'], meta['nlines'], order, engine=engine)
    meta = mergeMeta(meta)
    meta['shape'] = data.shape
    return meta, data

########################################################################################################
####General imaging parameters
# - Number of averages per frame
# - Average power
# - Frame rate
#####For each roi:
#     - XY center in mm
#     - XY size in mm
#     - XY pixels #
#     - list of z depths in mm

# Multiple scanfields per ROI, want to seperate into different ROIs

# when only one scanfield defined it is covers whole range

# when discrete plane mode only that plane defined

def loadMeta(path):
    files = glob(path)
    assert(len(files))
    with open(files[0]) as fid:
        header = json.load(fid)
    
    meta = parse(header)
    return meta

########################################################################################################

def parse(header):

    meta = {}
    assert(header['hRoiManager']['mroiEnable'])
    objectiveResolution = header['objectiveResolution']/1000

    if header['hFastZ']['enable']:
        depths = header['hFastZ']['userZs']
    else:
        depths = header['hStackManager']['zs']
    
    if type(depths) == int:
        meta['nplanes'] = 1
    else:
        meta['nplanes'] = len(depths)

    meta['depths'] = depths
    
    meta['averaging'] = header['hStackManager']['framesPerSlice']
    meta['power'] = header['hBeams']['powers']

    meta['volumeRate'] = header['hRoiManager']['scanFrameRate']

    meta['rois'] = [dict([('center', rescale(roi['scanfields']['centerXY'], objectiveResolution)),
            ('size', rescale(roi['scanfields']['sizeXY'], objectiveResolution)),
            ('npixels',roi['scanfields']['pixelResolutionXY']),
            ('depths', roi['zs'])]) 
             for roi in header['imagingRoiGroup']['rois']]
    meta['nrois'] = len(meta['rois'])
    meta['nlines'] = meta['rois'][0]['npixels'][1]
    
    meta['order'] = argsort([roi['center'][0] for roi in meta['rois']])
    meta['merge'] = check_order(meta['rois'], meta['order'])
    
    return meta

########################################################################################################

def rescale(x,FOVmm):
    return multiply(x,FOVmm).tolist()

########################################################################################################

def check_order(rois, order):
    diff = array([abs((rois[order[i]]['center'][0] + rois[order[i]]['size'][0]/2) 
    - (rois[order[i+1]]['center'][0] - rois[order[i+1]]['size'][0]/2)) for i in range(len(order)-1)])
    return diff.mean() < .02

########################################################################################################

def mergeMeta(meta):
    if meta['merge']:
        center = array([x['center'] for x in meta['rois']]).mean(axis=0)
        size = array([x['size'] for x in meta['rois']]).mean(axis=0)
        size[0] = size[0]*meta['nrois']
        npixels = array([x['npixels'] for x in meta['rois']]).mean(axis=0)
        npixels[0] = npixels[0]*meta['nrois']
        depths = array([x['depths'] for x in meta['rois']]).mean(axis=0)
        meta['rois'] = [dict([('center', list(center)),
            ('size', list(size)),
            ('npixels',list(npixels)),
            ('depths', depths)])]        
        meta['nrois'] = 1

    del meta['merge']
    del meta['order']
    del meta['nlines']
    
    return meta

########################################################################################################

def loadTiff(path, nplanes, nrois, nlines, order=False, engine=None):
    #Loads raw data from Tiff and reshapes
    data = thunder.images.fromtif(path, nplanes=nplanes, engine=engine) #17614 #34300
    return data.map(lambda x : reshape(x, nrois, nlines, order))


########################################################################################################

def split(oim, nrois, nlines):
    ## Takes a single 2-dim plane and reshapes it according to nrois, nlines
    assert oim.ndim == 2
    
    if nrois > 1:
        ntotal = oim.shape[0]
        ngap = (ntotal - nlines*nrois)/(nrois-1)
        return array([oim[nlines*i + ngap*i: nlines*(i + 1) + ngap*i, :] for i in range(nrois)])
    else:
        return oim

########################################################################################################

def merge(oim, order):
    ## Takes a single 3-dim volume and merges along x dimension into a single plane
    if type(order) != bool:
        assert oim.ndim == 3
        assert len(order) == oim.shape[0]
        return oim[order].transpose((1, 0, 2)).reshape([oim.shape[1], -1])
    else:
        return oim

########################################################################################################

def reshape(oim, nrois, nlines, order):
    ## Takes a 2-dim plane / 3-dim volume and splits and merges
    if oim.ndim == 3:
        return array(map(lambda x : merge(split(x, nrois, nlines), order), oim))
    else:
        return merge(split(oim, nrois, nlines), order)