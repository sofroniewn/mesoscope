import mesoscope as ms

data, metadata = ms.load('test/resources')
newdata, newmetadata = ms.convert(data, metadata)

print data.shape
print newdata.shape