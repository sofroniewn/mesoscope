from numpy import array, multiply, argsort
from glob import glob
import json
from os.path import join

def load(path):
    """
    Load metadata.
    """
    if not path.endswith('json'):
        path = join(path, '*.json')
    files = glob(path)
    if len(files) < 1:
        raise Exception('cannot find metadata file at %s' % path)
    with open(files[0]) as fid:
        header = json.load(fid)
    meta = parse(header)
    return meta

def merge(meta):
    """
    Merge metadata.
    """
    meta = meta.copy()
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

def parse(header):
    """
    Parse metadata from header dictionary.
    """
    meta = {}
    
    if not header['hRoiManager']['mroiEnable']:
        raise Exception('missing mroiEnable field')

    objective_resolution = header['objectiveResolution']/1000

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

    meta['rois'] = [dict([('center', rescale(roi['scanfields']['centerXY'], objective_resolution)),
            ('size', rescale(roi['scanfields']['sizeXY'], objective_resolution)),
            ('npixels',roi['scanfields']['pixelResolutionXY']),
            ('depths', roi['zs'])]) 
             for roi in header['imagingRoiGroup']['rois']]
    meta['nrois'] = len(meta['rois'])
    meta['nlines'] = meta['rois'][0]['npixels'][1]

    if type(header['hChannels']['channelSave']) == int:
        meta['nchannels'] = 1
    else:
        meta['nchannels'] = len(header['hChannels']['channelSave'])
    
    meta['order'] = argsort([roi['center'][0] for roi in meta['rois']])
    meta['merge'] = check_order(meta['rois'], meta['order'])
    
    return meta

def check_order(rois, order):
    """
    Check order.
    """
    diff = array([abs((rois[order[i]]['center'][0] + rois[order[i]]['size'][0]/2) 
    - (rois[order[i+1]]['center'][0] - rois[order[i+1]]['size'][0]/2)) for i in range(len(order)-1)])
    
    return diff.mean() < .02

def rescale(x, fovmm):
    """
    Rescale volume.
    """
    return multiply(x, fovmm).tolist()
