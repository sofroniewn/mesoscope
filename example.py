
#initializes directory structure,
#creates empty folders
from mesoscope.preprocess import init
init(path)

#load in raw scanimage tiffs and meta.json file,
#reshapes and merges data when appropriate
from mesoscope.preprocess import loadImages
meta, raw = loadImages(path, engine)


#normalize stack
from mesoscope.utils import normalize
norm = normalize(stack)


# mean = data.mean().toarray()
# data.tobinary(path)
# with open(savepath + '/meta-' + prefix + '.json', 'w') as fid:
#     json.dump(meta, fid, indent=2)
# normalize(mean)

##############################################################

#load in raw behaviour csvs,
#and concatenate across trials
from mesoscope.preprocess import loadTables
session = loadTables(path, engine)

#combine imaging and behavior variables,
#and downsample behaviour
from mesoscope.preprocess import combine
covariates = combine(info, session)

#drop bad trials from on disk data
from mesoscope.preprocess import drop
drop(path, trials)

##############################################################

#drop bad trials from on disk data
from mesoscope.images import register
corrected = register(raw, meta, method)




drop(path, trials)