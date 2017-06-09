import p05tools
import time
import tomopy
import dxchange
import logging
import numpy


################################
#   User:
#   AppID:
#   Sample:


################################
# Script Initialization

t0 = time.time()

scanname = 'INF_T1_200mPsBr_005a_s01a'
application_number = 11002139

rawdir, recodir = p05tools.reco.get_paths(scanname, application_number=application_number, year=2016)
p05tools.file.mkdir(recodir)

p05tools.reco.init_filelog(application_number, scanname, recodir)
logger = logging.getLogger('reco_logger.call_script')
logger.info('raw dir: {}'.format(rawdir))
logger.info('reco dir: {}'.format(recodir))

scanlog = p05tools.file.parse_scanlog(rawdir + scanname + 'scan.log')


################################
# tomopy options
ncore = 40
nchunk = 3


################################
# Projection preprocessing

proj, flat, dark, theta = p05tools.reco.get_rawdata(scanlog, rawdir, verbose=True)

binlevel = 1    # in powers of 2
pshape = proj.shape
print(pshape)
proj = tomopy.misc.morph.downsample(proj, binlevel, axis=1)
proj = tomopy.misc.morph.downsample(proj, binlevel, axis=2)
flat = tomopy.misc.morph.downsample(flat, binlevel, axis=1)
flat = tomopy.misc.morph.downsample(flat, binlevel, axis=2)
dark = tomopy.misc.morph.downsample(dark, binlevel, axis=1)
dark = tomopy.misc.morph.downsample(dark, binlevel, axis=2)
print('man')
logger.info('rebinned proj from {} to {}'.format(pshape, proj.shape))

proj = tomopy.prep.normalize.normalize(proj, flat, dark)

logger.info('normalized proj')

proj = tomopy.minus_log(proj)
logger.info('logarithmized proj')


################################
# Rotation center

rcen = False
auto_rcen = True
manual_rcen = False

if manual_rcen:
    # find rotation center manually by varying the rcen and writing back to file. Exits script when done.
    rcen_range = [754, 764, 0.1]
    tomopy.write_center(proj, theta, dpath = recodir + 'tmp/center', cen_range=rcen_range)
    logger.info('Reconstructed with varying rotation center from %g to %g in %g steps.' % (rcen_range[0], rcen_range[1], rcen_range[2]))
    raise SystemExit(0)

if auto_rcen:
    rcen_tol = 0.08
    logger.info('determine rotation center with tolerance: %g' % rcen_tol)
    rcen = tomopy.find_center(proj, theta, tol=rcen_tol)
    logger.info('found rotation center at %g px' % rcen)
    if rcen - proj.shape[2] > 20:
        logger.warning('rotation center more than 20px from projection center.')


################################
# Reduce dataset
#
nslice = 10
slices = [numpy.int(i*proj.shape[1]/nslice) for i in numpy.arange(1,10)]
proj = proj[:, slices, :]
logger.info('reduced proj stack to {} slices at {}'.format(nslice, slices))
# or use a single slice
# slicenum =750
# proj = proj[:, slicenum, :]
# proj = proj[:,numpy.newaxis,:]


################################
# Absorption contrast Reconstruction
#

reco_algorithm = 'gridrec'
reco = tomopy.recon(proj, theta, center=rcen, algorithm=reco_algorithm, ncore=ncore, nchunk=nchunk)
logger.info('reconstructed absorption data proj with algorithm: %s' % reco_algorithm)


################################
# Post processing

circ_mask_ratio = 1.0

reco = tomopy.circ_mask(reco, axis=0, ratio=circ_mask_ratio)
logger.info('applied circular mask with ratio: %s' % circ_mask_ratio)

reco = tomopy.remove_ring(reco, ncore=ncore, nchunk=nchunk)
logger.info('removed rings from reco with standard settings.')


################################
# Save data to disk
subdirectory = ''

# dxchange.write_tiff(reco, recodir + subdirectory + scanname + str(alpha), overwrite=True)
dxchange.write_tiff_stack(reco, recodir + subdirectory + scanname, overwrite=True)
logger.info('saved reco to directory: %s' % (recodir + subdirectory + scanname))

################################
# finish reconstruction

logger.info('DONE.')
t1 = time.time()
logger.info('Elapsed time: %g min.' % ((t1-t0)/60.0))

