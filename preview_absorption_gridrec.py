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

scanname = ''
application_number =
foldername = ''

rawdir, recodir = p05tools.reco.get_paths(scanname, foldername=foldername, application_number=application_number, year=2016)
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

use_preprocessed_projs = False

if use_preprocessed_projs:
    proj = dxchange.read_hdf5(recodir + 'norm.h5', 'exchange/data')
    theta = dxchange.read_hdf5(recodir + 'theta.h5', 'exchange/data')
    logger.info('loaded proj from file: %s' % (recodir + 'norm.h5'))
    logger.info('loaded theta from file: %s' % (recodir + 'theta.h5'))
else:
    proj, flat, dark, theta = p05tools.reco.get_rawdata(scanlog, rawdir, verbose=True)

    binfactor = 2
    proj = p05tools.reco.rebin_stack(proj, binfactor, descriptor='proj')
    flat = p05tools.reco.rebin_stack(flat, binfactor, descriptor='flat')
    dark = p05tools.reco.rebin_stack(dark, binfactor, descriptor='dark')

    # correlate flats and save array with related proj/flats
    corr_flat = p05tools.reco.correrlate_flat(proj, flat, verbose=True)
    dxchange.write_hdf5(corr_flat, fname=recodir + 'corr_flat.h5', overwrite=True)
    logger.info('saved corr_flat array to file: %s' % (recodir + 'corr_flat.h5'))

    # read correlated flats
    # corr_flat = dxchange.read_hdf5(recodir + 'corr_flat.h5', 'exchange/data')
    # logger.info('loaded from file: %s' % (recodir + 'corr_flat.h5'))

    proj = p05tools.reco.normalize_corr(proj, flat, dark, corr_flat, ncore=ncore)
    logger.info('logarithmized proj')

    proj = tomopy.minus_log(proj)
    logger.info('logarithmized proj')

    dxchange.write_hdf5(proj, fname=recodir + 'norm.h5', overwrite=True)
    dxchange.write_hdf5(theta, fname=recodir + 'theta.h5', overwrite=True)


################################
# Rotation center

rcen = False
auto_rcen = False
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
# skip = 770
# proj = proj[:, ::skip, :]
# theta = theta[::skip]
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
subdirectory = 'reco/'

# dxchange.write_tiff(reco, recodir + subdirectory + scanname + str(alpha), overwrite=True)
dxchange.write_tiff_stack(reco, recodir + subdirectory + scanname, overwrite=True)
logger.info('saved reco to directory: %s' % (recodir + subdirectory + scanname))

################################
# finish reconstruction

logger.info('DONE.')
t1 = time.time()
logger.info('Elapsed time: %g min.' % ((t1-t0)/60.0))

