import os
import json
import click
from os import mkdir
from numpy import inf
from glob import glob
from shutil import rmtree
from os.path import join, isdir, isfile
from thunder.images import fromtif, frombinary
from skimage.io import imsave
from .. import downsample
from showit import image
import matplotlib.animation as animation
import matplotlib.pyplot as plt

@click.option('--overwrite', is_flag=True, help='Overwrite if directory already exists')
@click.option('--localcorr', is_flag=True, help='Compute local correlation')
@click.option('--mean', is_flag=True, help='Compute mean')
@click.option('--movie', is_flag=True, help='Compute movie')
@click.option('--size', nargs=1, default=2, type=int, help='Int neighborhood for local correlation')
@click.option('--ds',  nargs=1, default=None, type=int, help='Int spatial downsample factor')
@click.option('--dt', nargs=1, default=None, type=int, help='Int temporal downsample factor')
@click.argument('output', nargs=1, metavar='<output directory>', required=False, default=None)
@click.argument('input', nargs=1, metavar='<input directory>', required=True)
@click.command('summarize', short_help='create summary images', options_metavar='<options>')
def summarize_command(input, output, localcorr, mean, movie, ds, dt, size, overwrite):
    output = input + '_converted' if output is None else output
    status('reading data from %s' % input)
    if len(glob(join(input, '*.tif'))) > 0:
        data = fromtif(input)
    elif len(glob(join(input, '*.bin'))) > 0:
        data = frombinary(input)
    else:
        error('no tif or binary files found in %s' % input)
        return

    if not isdir(output):
        mkdir(output)

    if mean:
        if not isfile(join(output, 'mean.tif')) or overwrite:
            status('summarizing-mean')
            m = data.mean().toarray()
            imsave(join(output, 'mean.tif'), m.clip(0, inf).astype('uint16'), plugin='tifffile', photometric='minisblack')
        else:
            warn('mean.tif already exists and overwrite is false')

    if localcorr:
        if type(size) == tuple:
            name = 'localcorr-%s.tif' % ''.join(map(str,size))
        else:
            name = 'localcorr-%s.tif' % size
        if not isfile(join(output, name)) or overwrite:
            status('summarizing-localcorr')
            if len(lc.shape) == 4:
                size = (1, size, size)
            lc = data.localcorr(size)
            imsave(join(output, name), lc.astype('float32'), plugin='tifffile', photometric='minisblack')
        else:
            warn('%s already exists and overwrite is false' % name)

    if movie:
        if type(ds) == tuple:
            dsString = '-ds'.join(map(str,ds))
        elif ds == None:
            dsString = ''
        else:
            dsString = '-ds' + str(ds)
        if dt == None:
            dtString = ''
        else:
            dtString = '-dt' + str(dt)
        if len(data.shape) == 4:
            pString = '-p%s' % 0
        else:
            pString = ''
        name = 'movie%s%s%s.mp4' % (dsString, dtString, pString)
        if not isfile(join(output, name)) or overwrite:
            status('summarizing-movie')
            if len(data.shape) == 4:
                ds = (1, ds, ds)
            mv = downsample(data, ds=ds, dt=dt).toarray()
            if len(data.shape) == 4:
                for plane in range(mv.shape(3)):
                    pString = '-p%s' % plane
                    name = 'movie%s%s%s.mp4' % (dsString, dtString, pString)
                    print(name)
            else:
                print(name)

            clim = 100
            frame = mv.shape[0]/2
            img = mv[frame,:,:]

            fig = plt.figure(figsize=[12, 12.0*img.shape[0]/img.shape[1]])
            fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
            ax = plt.gca()
            im = image(img, clim=(0, clim*8), ax=ax)

            # time = ax.text(.97*img.shape[1], .04*img.shape[0], '%.1f s' % (frame/frameRate), color='white', fontsize=22, ha='right', fontdict={'family': 'monospace'});
            # ax.plot([.04*img.shape[1], .04*img.shape[1]+scaleBar*pixelsPerUm], [.94*img.shape[0], .94*img.shape[0]], 'w');
            # sclae = ax.text(.04*img.shape[1]+scaleBar*pixelsPerUm/2, .97*img.shape[0], '%d um' % scaleBar, color='white', fontsize=22, ha='center', fontdict={'family': 'monospace'});
            # plt.xlim([0, img.shape[1]]);
            # plt.ylim([img.shape[0], 0]);
            dsTime = 5
            nframes = mv.shape[0]-dsTime

                #time.set_text('%.1f s' % ((dsTime/2+frame)/frameRate))

            ani = animation.FuncAnimation(fig, update, nframes, blit=False)
            ani.save(join(output, name), writer=writer)














            # work on naming of movie, so if none ds, dt, use a 1
            # go through each plane and create movie
            # have to decide how to take clim, use percentile of mean ???, make commandline option??
            # check if metadata exists - if so load it in and use for timestamp / scalebar
#            imsave(join(output, name), lc.astype('float32'), plugin='tifffile', photometric='minisblack')
        else:
            warn('%s already exists and overwrite is false' % name)

    success('summary complete')

def success(msg):
    click.echo('[' + click.style('success', fg='green') + '] ' + msg)

def status(msg):
    click.echo('[' + click.style('convert', fg='blue') + '] ' + msg)

def error(msg):
    click.echo('[' + click.style('error', fg='red') + '] ' + msg)

def warn(msg):
    click.echo('[' + click.style('warn', fg='yellow') + '] ' + msg)

Writer = animation.writers['ffmpeg']
writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=40000)

def update(frame):
    im.set_array(movie[dsTime/2+frame,:,:])
