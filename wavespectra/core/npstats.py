"""Wave spectra stats on numpy arrays sourced by apply_ufuncs."""
import numpy as np


def hs(spectrum, freq, dir, tail=True):
    """Significant wave height Hmo.

    Args:
        - spectrum (2darray): wave spectrum array.
        - freq (1darray): wave frequency array.
        - dir (1darray): wave direction array.
        - tail (bool): if True fit high-frequency tail before integrating spectra.

    """
    df = abs(freq[1:] - freq[:-1])
    if len(dir) > 1:
        ddir = abs(dir[1] - dir[0])
        E = ddir * spectrum.sum(1)
    else:
        E = np.squeeze(spectrum)
    Etot = 0.5 * sum(df * (E[1:] + E[:-1]))
    if tail and freq[-1] > 0.333:
        Etot += 0.25 * E[-1] * freq[-1]
    return 4.0 * np.sqrt(Etot)


def dp(dirspec, dir):
    """Peak wave direction Dp.

    Args:
        - dirspec (1darray): Frequency-integrated wave spectrum array E(d).
        - freq (1darray): Wave frequency array.

    Returns:
        - dp (float): Direction of the maximum energy density in the
          frequency-integrated spectrum.

    """
    return dir[np.argmax(dirspec)]


def tps(spectrum, freq):
    """Smooth peak wave period Tp.

    Args:
        - spectrum (1darray): Direction-integrated wave spectrum array E(f).
        - freq (1darray): Wave frequency array.

    Returns:
        - tp (float): Period of the maximum energy density in the smooth spectrum.

    Note:
        - The smooth peak period is the peak of a parabolic fit around the spectral
          peak. It is the period commonly defined in SWAN and WW3 model output.

    """
    ipeak = fpeak(spectrum)
    if not ipeak:
        return None
    f1, f2, f3 = [freq[ipeak + i] for i in [-1, 0, 1]]
    e1, e2, e3 = [spectrum[ipeak + i] for i in [-1, 0, 1]]
    s12 = f1 + f2
    q12 = (e1 - e2) / (f1 - f2)
    q13 = (e1 - e3) / (f1 - f3)
    qa = (q13 - q12) / (f3 - f2)
    fp = (s12 - q12 / qa) / 2.0
    return 1.0 / fp


def tp(spectrum, freq):
    """Peak wave period Tp.

    Args:
        - spectrum (1darray): Frequency wave spectrum array E(f).
        - freq (1darray): Wave frequency array.

    Returns:
        - tp (float): Period of the maximum energy density in the frequency spectrum.

    """
    ipeak = fpeak(spectrum)
    if not ipeak:
        return None
    return 1.0 / freq[ipeak]


def fpeak(arr):
    """Returns the index of largest peak in the frequency spectrum.

    Args:
        - arr (1darray): Frequency spectrum.

    Returns:
        - ipeak (SpecArray): indices for slicing arr at the frequency peak.

    Note:
        - A peak is found when arr(ipeak-1) < arr(ipeak) < arr(ipeak+1).
        - Given the above, ipeak == 0 implies no peak has been detected.

    """
    ispeak = (np.diff(np.append(arr[0], arr)) > 0) & (
        np.diff(np.append(arr, arr[-1])) < 0
    )
    peak_pos = np.where(ispeak, arr, 0).argmax()
    return peak_pos

