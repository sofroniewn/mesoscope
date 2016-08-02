from thunder.images import fromtif

def load_images(path, nplanes, engine=None):
    images = fromtif(path, nplanes=nplanes, engine=engine)
    return images