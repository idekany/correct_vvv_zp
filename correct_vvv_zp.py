import numpy as np
import utils as ut
import os
import sys

# Read parameters from a file or from the command line:
parser = ut.argparser()
# print(len(sys.argv))
if len(sys.argv) == 1:
    # use default name for the parameter file
    pars = parser.parse_args([ut.default_parameter_file])
else:
    pars = parser.parse_args()

pars = ut.process_input_parameters(pars)

# Wired-in parameters:
sep = '\s+'         # separator character in the light curve files ('\s+' is any number of whitespaces)
comment = '#'       # comment character in the light curve files

# colname_mjd = 'mjd'
# colname_tile = 'tile'
# colname_obsid = 'obsid'
# colname_chip = 'chip'
# colname_pawid = 'ipaw'
# colname_obstime = 'hjd'
# colname_mag = 'mag'
# colname_magerr = 'magerr'

zpcorr_table = np.load(os.path.join(pars.rootdir, pars.input_table), encoding='bytes')

ids = np.genfromtxt(pars.input_list, dtype=None, unpack=False, comments='#', filling_values=np.nan, encoding='latin1')

n_object = len(ids)

for ilc, objname in enumerate(ids):

    filename = os.path.join(pars.rootdir, pars.lcdir, objname + pars.lcsuffix_in)
    lcdatain = ut.read_lc(filename, pars.colnames, usecols=pars.usecols, subset_expr=pars.subset,
                          sep=sep, comment=comment, verbose=pars.verbose)

    output_list = []

    ii = 0
    for iap in pars.apertures:

        mjd = lcdatain[pars.colname_mjd].to_numpy()
        tile = lcdatain[pars.colname_tile].to_numpy().astype(bytes)
        obsid = lcdatain[pars.colname_obsid].to_numpy().astype(bytes)
        ichip = lcdatain[pars.colname_chip].to_numpy()
        expnum = lcdatain[pars.colname_pawid].to_numpy()

        otime = lcdatain[pars.colname_obstime].to_numpy()
        mag = lcdatain[pars.colname_mag + str(iap)].to_numpy()
        magerr = lcdatain[pars.colname_magerr + str(iap)].to_numpy()

        mag, magerr, otime, zperr, tile, expnum, ichip, obsid, ndata, zpcorr_this_obj = \
            ut.correct_zp_by_obsid(zpcorr_table, obsid, iap, tile, expnum, ichip, mag, magerr, otime)

        if ii == 0:
            output_list.append(otime)
        output_list.append(mag)
        output_list.append(magerr)
        output_list.append(zperr)

        ii += 1

    output_arr = np.rec.fromarrays(output_list)
    fmt = "%.6f" + 3 * len(pars.apertures) * " %.3f"
    np.savetxt(os.path.join(pars.rootdir, pars.lcdir, objname + pars.lcsuffix_out), output_arr, fmt=fmt)
