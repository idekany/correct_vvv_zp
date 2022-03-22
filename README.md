# correct_vvv_zp

Correct_vvv_zp is a Python3 library for the correction of the photometric zero points (ZPs)
of the VISTA Variables in the Via Lactea ([VVV](https://vvvsurvey.org/)) ESO Public Survey,
using the method published by 
[Hajdu, Dekany, Catelan & Grebel (2020)](https://arxiv.org/abs/1908.06160).
Specifially, the program `correct_vvv_zp.py` applies the corrections from 
Table 1 of the corresponding [paper](https://arxiv.org/abs/1908.06160).

## Installation

Simply use `git clone <URL>` to clone this library into a local directory. 
Subsequently, it can be added to your `PYTHONPATH` either temporarily by 
issuing the `sys.path.append("/your/local/directory")` command in python,
or permanantly by exporting you directory into the `PYTHONPATH` system variable.
For example, if using the bash shell, add the 
`export PYTHONPATH="${PYTHONPATH}:/your/local/directory"` in the ~/.bashrc
file.

Extract the split gzipped tar archive of the binary numpy file `zpcorrtable.npy`:

`cat zpcorrtable.npy.tar.gz.* | tar xzvf -`

### Dependencies

This library was written and tested in the following python environment:
`python 3.8.10`, `numpy 1.19.5`, `pandas 1.3.0`.
We suggest to use this library in the same environment, created by a virtual environment manager 
such as [conda](https://docs.conda.io/en/latest/).

## Usage
The corrections are performed by the correct_vvv_zp.py program, 
that can be run using command-line arguments:

`python correct_vvv_zp.py [OPTION]`

or by supplying a parameter file that includes the command-line arguments:

`python correct_vvv_zp.py @<parameter_file>`

The full list of command-line options can be printed on the STDOUT by:

`python correct_vvv_zp.py --help`

An example parameter file `correct_vvv_zp.par` is also provided for convenience.

### Input
The program processes a list of photometric time series (light curves) stored in separate files, specified 
by the `--input_list <listfile>` parameter. Here, `<listfile>` must contain a single column with one filename
prefix per line (e.g., star identifiers). By default, each 
time series will be read from the file `./<lcdir>/<identifier><lcsuffix_in>`,
customizable by the `--lcdir` and the `--lcsuffix_in` parameters.

The ZP correction of each measurement is determined based on a number of 
metadata parameters that must be
provided for each data point in the light curve files. These are:

- VVV observation ID (e.g., `v20100319_00519`), suffices of the catalog filenames provided by 
[CASU](http://casu.ast.cam.ac.uk/);
- VIRCAM aperture number [1..5];
- VVV tile identifier, e.g., 'b308';
- VIRCAM exposure number, i.e., "HIERARCH ESO DET EXP NO" value in the CASU FITS 
  catalog files' headers.
  This is an identifier of each (dithered) single VIRCAM exposure (a.k.a. 'pawprint');
- VIRCAM chip number [1..16];
- Modified Julian Date of the observation (MJD-OBS value in the catalog/image headers).

The input light-curve files should contain at least the following columns 
separated by any number of 
whitespaces, with their default names provided in parentheses.
The required columns are:

VVV observation ID _(obsid)_, VVV tile identifier _(tile)_, VIRCAM chip number _(chip)_, 
VIRCAM exposure number _(expnum)_, Modified Julian Date of the observation _(mjd)_, 
Observation time _(hjd)_, magnitude _(mag1)_, magnitude error _(magerr1_)

The input light curve files are highly customizable with the following command-line parameters:

`--usecols <list of column indices>` specifies which columns to consider in the input files;

`--colnames <list of column names>` specifies the custom names of the considered columns;

`--apertures <list of apertures>` specifies which apertures to consider;

`--subset <criteria>` specifies custom threshold-rejection criteria in the pandas.dataframe.query format.

If the names of the required columns (see above) differ from the default ones 
_(shown in parentheses)_,
these must be explicitly specified by the following parameters:
`--colname_obsid`, `--colname_tile`, , `--colname_chip`, 
`--colname_expnum`, `--colname_mjd`, `--colname_obstime`, `--colname_mag`, and `--colname_magerr`.

### Output

The ZP-corrected light curves are written into the the following files:
`./<lcdir>/<identifier><lcsuffix_out>`, where `<identifier>` matches that of the 
corresponding input file.

The output files have the following columns: observation time (matching the column 
named by `--colname_obstime`, _hjd_ by default), followed by the corrected magnitude,
its statistical uncertainty, and its ZP error, repeated for each aperture.

### Examples

A few example uncorrcected VVV light curve files are provided in the `test_data` subdirectory. 
The input list file `input.lst` contains the corresponding identifiers, 
and the `correct_vvv_zp.par` contains the parameter settings necessary to 
correctly process these files.

Try the code with the supplied data and parameter file by the following command:

`python correct_vvv_zp.py @correct_vvv_zp.par`

The resulting corrected data files can be found in the `test_data` directory. 
Their content should match the corresponding `*.dat~` files. 

## Citation

If this library is used in an astronomical research project as provided here or in a
modified form, we kindly ask the author to cite the following paper in the resulting publication:

```angular2html
@ARTICLE{2020ExA....49..217H,
       author = {{Hajdu}, Gergely and {D{\'e}k{\'a}ny}, Istv{\'a}n and {Catelan}, M{\'a}rcio and {Grebel}, Eva K.},
        title = "{On the optimal calibration of VVV photometry}",
      journal = {Experimental Astronomy},
     keywords = {Photometric calibration, Near-infrared photometry, VISTA, Photometric zero points, Astrophysics - Instrumentation and Methods for Astrophysics, Astrophysics - Astrophysics of Galaxies, Astrophysics - Solar and Stellar Astrophysics},
         year = 2020,
        month = jun,
       volume = {49},
       number = {3},
        pages = {217-238},
          doi = {10.1007/s10686-020-09661-0},
archivePrefix = {arXiv},
       eprint = {1908.06160},
 primaryClass = {astro-ph.IM},
       adsurl = {https://ui.adsabs.harvard.edu/abs/2020ExA....49..217H},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}
```

## License

[MIT](https://choosealicense.com/licenses/mit/), see `LICENSE`.