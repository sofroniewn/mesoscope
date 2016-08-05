import mesoscope as ms

data, metadata = ms.load('test/resources/input')
newdata, newmetadata = ms.convert(data, metadata)

print('shape before conversion')
print(data.shape)
print('shape after conversion')
print(newdata.shape)