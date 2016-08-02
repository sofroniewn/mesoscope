import mesoscope as ms

data, metadata = ms.load('test/resources')
processed = ms.convert(data, metadata)