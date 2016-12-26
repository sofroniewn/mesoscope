from numpy import pad, zeros, ceil, floor
from thunder.images import fromarray
from registration import CrossCorr

def correct(data, amount=None):
    if len(data.shape) == 3:
        img = data[data.shape[0]/2].toarray()
        if amount==None:
            amount = estimate(img)
        return data.map(lambda x: shift(x, amount)), amount
    elif len(data.shape) == 4:
        img = data.mean().toarray()
        img = img[img.shape[0]/2]
        if amount==None:
            amount = estimate(img)
        return data.map(lambda x: map(lambda y: shift(y, amount), x)), amount
    else:
        print('Data length %d currently not supported' % len(data.shape))

def correct_plane(img, amount=None):
    if amount==None:
        amount = estimate(img)
    return shift(img, amount)

def estimate(img):
    even = img[0:-2:2,:]
    odd = img[1:-1:2,:]
    algorithm = CrossCorr()
    model = algorithm.fit(even, odd)
    return model.toarray()[0][1]

def shift(img, amount):
    if amount == 0:
        return img
    elif amount > 0:
        img_shift = zeros(img.shape)
        img_shift[0:-1:2,:] = lateral_shift(img[0:-1:2,:],ceil(amount/2.0).astype(int),left=True)
        img_shift[1:-1:2,:] = lateral_shift(img[1:-1:2,:],floor(amount/2.0).astype(int),left=False)
        return img_shift
    else:
        amount = -amount
        img_shift = zeros(img.shape)
        img_shift[1:-1:2,:] = lateral_shift(img[1:-1:2,:],ceil(amount/2.0).astype(int),left=True)
        img_shift[0:-1:2,:] = lateral_shift(img[0:-1:2,:],floor(amount/2.0).astype(int),left=False)
        return img_shift

def lateral_shift(img, amount, left=False):
    if amount == 0:
        return img
    else:
        if left:
            return pad(img, ((0, 0), (0, amount)), 'edge')[:,amount:]
        else:
            return pad(img, ((0, 0), (amount, 0)), 'edge')[:,:-amount]
