import csv
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import sys
sys.dont_write_bytecode = True

import config

# =====================================================================================
# Private methods
# =====================================================================================

def _saveToPdf(output):
    pp = PdfPages(output)
    plt.savefig(pp, format='pdf')
    pp.close()
    plt.close()

# Manipulate y-axis of histogarm
def _to_percent(y, position):
    # tick locations calculated from fraction (global).
    s = str(y*100)
    # The percent symbol needs escaping in latex
    if matplotlib.rcParams['text.usetex'] == True:
        return s + r'$\%$'
    else:
        return s + '%'

# Calc min, max position of each histogram bin
def _minRuler(array):
    minimum = min(array)
    print " - min: ", minimum
    offset = minimum % step
    return minimum - offset

def _maxRuler(array):
    maximum = max(array)
    print " - max: ", maximum
    offset = maximum % step
    return maximum - offset + step

# =====================================================================================
# Start main methods (tools)
# =====================================================================================

# Input: x.dat from global variables (config) or arguments
# Output: histogram. x.pdf
# Histogram settings are configurable through config.py
def draw_histogram(*target, **kwargs):
    if len(target) == 1:
        target = target[0]
        assert type(target) == list
        file_list = target
    else:
        file_list = config.weight_all
    global step
    step = kwargs["step"]

    for target in file_list:
        print "Target: ", target
        try:
            with open(config.pdf_prefix+"%s" % target) as text:
                x = np.float32(text.read().rstrip("\n").split("\n"))

            # norm = np.ones_like(x) / float(len(x))
            norm = np.ones_like(x)
            binspace = np.arange(_minRuler(x), _maxRuler(x), step)
            n, bins, patches = plt.hist(x, bins=binspace, weights=norm,
                alpha=config.alpha, facecolor=config.color)

            # formatter = FuncFormatter(_to_percent)
            # plt.gca().yaxis.set_major_formatter(formatter)
            plt.grid(True)

            _saveToPdf(config.pdf_prefix+"%s.pdf" % target.split(".")[0])
        except IOError as e:
            print "Warning: I/O error({0}) - {1}".format(e.errno, e.strerror)
            pass
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
    print "Graphs are drawned!"

# Input: model object list, Output: human-readable form of model as x.dat
def print_weight_vars(obj_dict, weight_obj_list, fname_list, show_zero=False):
    for elem, fname in zip(weight_obj_list, fname_list):
        weight_arr = obj_dict[elem].eval()
        ndim = weight_arr.size
        flat_weight_space = weight_arr.reshape(ndim)
        with open(fname, "w") as filelog:
            if show_zero == False:
                flat_weight_space = flat_weight_space[flat_weight_space != 0]
            writeLine = csv.writer(filelog, delimiter='\n')
            writeLine.writerow(flat_weight_space)

# Input: synapse, Output: human-readable form of model as x.syn
def print_synapse_nps(syn_arr, fname, show_zero=False):
    ndim = syn_arr.size
    flat_syn_space = syn_arr.reshape(ndim)
    with open(fname, "w") as filelog:
        if show_zero == False:
            flat_syn_space = flat_syn_space[flat_syn_space != 0]
        writeLine = csv.writer(filelog, delimiter='\n')
        writeLine.writerow(flat_syn_space)

# Input: sparse model object list, Output: human-readable form of model as x.dat
def print_sparse_weight_vars(obj_dict, weight_obj_list, fname_list):
    for elem, fname in zip(weight_obj_list, fname_list):
        weight_arr = obj_dict[elem].eval().values
        ndim = weight_arr.size
        flat_weight_space = weight_arr.reshape(ndim)
        with open(fname, "w") as filelog:
            writeLine = csv.writer(filelog, delimiter='\n')
            writeLine.writerow(flat_weight_space)

# Input: n-d dense array, Output: pruned array with threshold
def prune_dense(weight_arr, name="None", thresh=0.005, **kwargs):
    """Apply weight pruning with threshold """
    under_threshold = abs(weight_arr) < thresh
    weight_arr[under_threshold] = 0
    count = np.sum(under_threshold)
    print "Non-zero count (%s): %s" % (name, weight_arr.size - count)
    return weight_arr, ~under_threshold, count

# Input: anonymous dimension array and its pruning threshold,
# Output: indices - index list of non-zero elements
#         values  - value list of non-zero elements
#         shape   - original shape of matrix
def prune_tf_sparse(weight_arr, name="None", thresh=0.005):
    assert isinstance(weight_arr, np.ndarray)

    under_threshold = abs(weight_arr) < thresh
    weight_arr[under_threshold] = 0
    values = weight_arr[weight_arr != 0]
    indices = np.transpose(np.nonzero(weight_arr))
    shape = list(weight_arr.shape)

    count = np.sum(under_threshold)
    print "Non-zero count (Sparse %s): %s" % (name, weight_arr.size - count)
    return [indices, values, shape]

# Input: file name and text, Output: log file
def log(fname, log):
   with open(fname, "a") as wobj:
        wobj.write(str(log)+"\n")

# Input: Path to target image, Output: ndarray resized to fixed (28,28)
def imread(path):
    import numpy as np
    import Image
    return np.array(Image.open(path).resize((28,28), resample=2))
