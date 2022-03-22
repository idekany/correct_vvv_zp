import numpy as np
import pandas as pd
import argparse
import os

default_parameter_file = '@correct_vvv_zp.par'


def read_lc(filename: str, colnames: list, usecols: list = None, subset_expr: str = None,
            sep: str = '\s+', comment: str = '#', verbose: bool = True):
    """
    Read in a light curve file and perform threhold rejections on the data.

    :param filename: name of the input light curve file
    :param colnames: list of column names to be used (must match `usecols` if provided)
    :param usecols: list of column indices to be used (must match `colnames`, default: None)
    :param subset_expr: expression for threshold rejection in pandas dataframe query format
    :param sep: separator character between columns (default: "\s+")
    :param comment: starting character of comment lines (default: "#")
    :param verbose: verbosity (default: True)
    :return: pandas dataframe object
    """

    df = pd.read_csv(filename, names=colnames, usecols=usecols, header=None, sep=sep, comment=comment)
    ndata = len(df)
    if verbose:
        print("{} lines read from {} ; ".format(ndata, filename), end='')
    if subset_expr is not None:
        df = df.query(subset_expr)
        ndata = len(df)
        if verbose:
            print("{} lines after threshold rejection".format(ndata))

    return df


def correct_zp_by_obsid(corr_table, obsid, aperture, tile, ipaw, ichip, mag, magerr, otime):
    """
    Performs ZP corrections of VVV photometry of a vector of magnitudes.

    :param corr_table: table of ZP corrections (Hajdu et. al 2020)
    :param obsid: unique identifier of the observation (e.g., 'v20100411_01112')
    :param aperture: VIRCAM aperture, element of {1,2,3,4,5}
    :param tile: tile identifier (e.g., 'b283')
    :param ipaw: pawprint identifier
    :param ichip: number of VIRCAM chip, 1..16
    :param mag: magnitude value
    :param magerr: photometric error
    :param otime: observation time (HJD)
    :return: mag, magerr, otime, zperr, ipaw, ichip, obsid, ndata, zpcorr_this_obj
    """
    # First, select the subset of the correction table for the relevant tile(s):
    aper = str(aperture)
    corr_table_subset = corr_table[np.isin(corr_table['field'], tile)]
    a = np.column_stack((corr_table_subset['obsid'], corr_table_subset['chip']))
    b = np.column_stack((obsid, ichip))
    data_indx, corr_indx = np.where((a == b[:, None]).all(-1))
    # data_indx : index array of the input arrays that have matching correction values in corr_table
    # corr_indx : index array of corr_table corresponding to mag[dataindx]
    zpcorr_this_obj = corr_table_subset[corr_indx]['ap' + aper]
    # zpcorrerr_this_obj = corr_table_subset[corr_indx]['sig'+aper]
    # zpcorrnstar_this_obj = corr_table_subset[corr_indx]['Nstar']
    zperr = corr_table_subset[corr_indx]['zperr' + aper]
    # zpcorrerr_this_obj = zpcorrerr_this_obj / np.sqrt(zpcorrnstar_this_obj)
    mag = mag[data_indx] - zpcorr_this_obj
    magerr = magerr[data_indx]
    ipaw = ipaw[data_indx]
    ichip = ichip[data_indx]
    otime = otime[data_indx]
    tile = tile[data_indx]
    obsid = obsid[data_indx]
    ndata = len(data_indx)

    return mag, magerr, otime, zperr, tile, ipaw, ichip, obsid, ndata, zpcorr_this_obj


def argparser():
    """
    Creates an argparse.ArgumentParser object for reading in parameters from a file.
    :return: parameter object
    """
    ap = argparse.ArgumentParser(fromfile_prefix_chars='@',
                                 description='Correct the photometric zero point of VVV data.',
                                 epilog="")

    # use custom line parser for the parameter file
    ap.convert_arg_line_to_args = convert_arg_line_to_args

    ap.add_argument('--rootdir',
                    action='store',
                    type=str,
                    default=os.path.expanduser('~'),
                    help='Full path of the root directory '
                         '(all other directory and file names will be relative to this, default: `~`).')

    ap.add_argument('--input_table',
                    action='store',
                    type=str,
                    default=os.path.expanduser('zpcorrtable.npy'),
                    help='Binary table with the ZP corrections (default: zpcorrtable.npy).')

    ap.add_argument('--input_list',
                    action='store',
                    type=str,
                    default=os.path.expanduser('input.lst'),
                    help='Input list file of identifiers (default: input.lst).')

    ap.add_argument('--lcdir',
                    action='store',
                    type=str,
                    default=os.path.expanduser('data'),
                    help='Subdirectory of input light curves (default: data).')

    ap.add_argument('--lcsuffix_in',
                    action='store',
                    type=str,
                    default=os.path.expanduser('.dat'),
                    help='Suffix of the input light curve files (default: .dat). '
                         'Files will be searched as: ./<lcdir>/<id><lcsuffix_in>, '
                         'where <id> is read from <input_list>.')

    ap.add_argument('--lcsuffix_out',
                    action='store',
                    type=str,
                    default=os.path.expanduser('.dat'),
                    help='Suffix of the output light curve files (default: .dat). '
                         'Files will be saved as: ./<lcdir>/<id><lcsuffix_out>, '
                         'where <id> is read from <input_list>.')

    ap.add_argument('--usecols',
                    action='store',
                    nargs='*',
                    type=int,
                    default=None,
                    help='List of the numbers of data columns to use in the light curve files (default: all columns).')

    ap.add_argument('--colnames',
                    action='store',
                    nargs='*',
                    type=str,
                    default=None,
                    help='List of the names of data columns to use in the light curve files '
                         '(default: all columns).')

    ap.add_argument('--apertures',
                    action='store',
                    nargs='*',
                    type=int,
                    default=None,
                    help='List of apertures [1..5] to use (default: all apertures).')

    ap.add_argument('--subset',
                    action='store',
                    type=str,
                    nargs='*',
                    help='Expression for subsetting the input data, following the pandas dataframe query format.')

    ap.add_argument('--colname_mjd',
                    action='store',
                    type=str,
                    default=os.path.expanduser('mjd'),
                    help='Name of the column of Modified Julian Date (MJD) (default: mjd).')

    ap.add_argument('--colname_tile',
                    action='store',
                    type=str,
                    default=os.path.expanduser('tile'),
                    help='Name of the column of VVV tile identifiers (default: tile).')

    ap.add_argument('--colname_obsid',
                    action='store',
                    type=str,
                    default=os.path.expanduser('obsid'),
                    help='Name of the column of VVV observation ID (default: obsid).')

    ap.add_argument('--colname_chip',
                    action='store',
                    type=str,
                    default=os.path.expanduser('chip'),
                    help='Name of the column of VIRCAM chip number (default: chip).')

    ap.add_argument('--colname_expnum',
                    action='store',
                    type=str,
                    default=os.path.expanduser('expnum'),
                    help='Name of the column of VIRCAM exposure number (default: expnum).')

    ap.add_argument('--colname_obstime',
                    action='store',
                    type=str,
                    default=os.path.expanduser('hjd'),
                    help='Name of the column of the observation time (default: hjd).')

    ap.add_argument('--colname_mag',
                    action='store',
                    type=str,
                    default=os.path.expanduser('mag'),
                    help='Name prefix of the magnitude columns (default: mag). '
                         'The aperture number will be appended to the value given here, e.g., mag1, mag2, ...')

    ap.add_argument('--colname_magerr',
                    action='store',
                    type=str,
                    default=os.path.expanduser('magerr'),
                    help='Name prefix of the magnitude error columns (default: magerr). '
                         'The aperture number will be appended to the value given here, e.g., magerr1, magerr2, ...')

    ap.add_argument('-v',
                    '--verbose',
                    action='store_true',  # assign True value if used
                    help='Generate verbose output.')

    return ap


def process_input_parameters(pars):

    if pars.colnames is None:
        pars.colnames = ['obsid', 'tile', 'chip', 'expnum', 'mjd', 'hjd', 'mag1', 'magerr1']

    if pars.apertures is None:
        pars.apertures = [1, 2, 3, 4, 5]
    else:
        # check if there are repeating elements:
        assert len(pars.apertures) == len(set(pars.apertures))
        for ap in pars.apertures:
            assert ap in [1, 2, 3, 4, 5], "`apertures` must be a list of unique integers between 1 and 5"

    # Join the list elements of pars.subset into a long string:
    if pars.subset:
        pars.subset = ' '.join(pars.subset)

    return pars


def convert_arg_line_to_args(arg_line):
    """
    Custom line parser for argparse.
    :param arg_line: str
    One line of the input parameter file.
    :return: None
    """
    if arg_line:
        if arg_line[0] == '#':
            return
        for arg in arg_line.split():
            if not arg.strip():
                continue
            if '#' in arg:
                break
            yield arg
