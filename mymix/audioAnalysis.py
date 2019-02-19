import os
import wave
import sys
from mymix import app
from matplotlib import pyplot as plt
import numpy as np
import scipy.signal



    
def generate_plots():

    path1 = os.path.join(app.root_path, 'public/generated_plots', 'plot1.png')
    path2 = os.path.join(app.root_path, 'public/generated_plots', 'plot2.png')
    path3 = os.path.join(app.root_path, 'public/generated_plots', 'optimal_path.png')
    try:
        os.remove(path1)
        os.remove(path2)
        os.remove(path3)
    except:
        pass

    fs = 22050.

    snd = []
    for filename in os.listdir(os.path.join(app.root_path, 'public/uploaded_audio_files')):
        snd.append(load_wav(os.path.join(app.root_path, 'public/uploaded_audio_files', filename)))

    fft_len = 4096
    hop_size = fft_len // 4

    if len(snd) != 2:
        return ""

    chroma_x = make_chromagram(snd[0], fs, fft_len, hop_size, normalize=False)
    chroma_x = cens(chroma_x, 11, 4)

    chroma_y = make_chromagram(snd[1], fs, fft_len, hop_size, normalize=False)
    chroma_y = cens(chroma_y, 11, 4)

    plt.rcParams['figure.figsize'] = (12, 2)
    plt.imshow(chroma_x, aspect="auto", origin='lower',cmap='gray_r')
    plt.colorbar()
    plt.yticks([0,5,10])
    plt.title('Chromagram from audio file 1')

    plt.savefig(os.path.join(app.root_path, 'public/generated_plots/plot1'))

    plt.rcParams['figure.figsize'] = (12, 2)
    plt.imshow(chroma_y, aspect="auto", origin='lower',cmap='gray_r')
    plt.title('Chromagram from audio file 2')

    plt.savefig(os.path.join(app.root_path, 'public/generated_plots/plot2'))
    
    cost = make_cost_matrix(chroma_x, chroma_y)
    path = dtw(cost, simple_steps_w(.8))[1]
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.figure()
    plt.imshow(cost, origin='lower')
    plt.xlabel('audio file 2')
    plt.ylabel('audio file 1')
    plt.title('The optimal correspondence between the two audio files')
    plt.colorbar()
    plt.plot(path[:,1], path[:,0], '-r', linewidth=3)

    plt.savefig(os.path.join(app.root_path, 'public/generated_plots/optimal_path'))

    path1 = os.path.join(app.root_path, 'public/uploaded_audio_files', 'audio_file_1.wav')
    path2 = os.path.join(app.root_path, 'public/uploaded_audio_files', 'audio_file_2.wav')

    os.remove(path1)
    os.remove(path2)

    return "success"


def load_wav(filepath, t_start = 0, t_end = sys.maxsize, only_22k = True) :
    """Load a wave file, which must be 22050Hz and 16bit and must be either
    mono or stereo. 
    Inputs:
        filepath: audio file
        t_start, t_end:  (optional) subrange of file to load (in seconds)
        only_22k: if True (default), assert if sample rate is different from 22050.
    Returns:
        a numpy floating-point array with a range of [-1, 1]
    """
    
    wf = wave.open(filepath)
    num_channels, sampwidth, fs, end, comptype, compname = wf.getparams()
    
    # for now, we will only accept 16 bit files at 22k
    assert(sampwidth == 2)
    # assert(fs == 22050)

    # start frame, end frame, and duration in frames
    f_start = int(t_start * fs)
    f_end = min(int(t_end * fs), end)
    frames = f_end - f_start

    wf.setpos(f_start)
    raw_bytes = wf.readframes(frames)

    # convert raw data to numpy array, assuming int16 arrangement
    samples = np.fromstring(raw_bytes, dtype = np.int16)

    # convert from integer type to floating point, and scale to [-1, 1]
    samples = samples.astype(np.float)
    samples *= (1 / 32768.0)

    if num_channels == 1:
        return samples

    elif num_channels == 2:
        return 0.5 * (samples[0::2] + samples[1::2])

    else:
        raise('Can only handle mono or stereo wave files')




def make_chromagram(x, fs, fft_len, hop_size, normalize = True, gamma = 0, tuning=0.) :
    """Return chromagram of signal x
        x: signal
        fs: sample rate
        fft_len: length of FFT
        hop_size: hop_size for STFT 
        gamma: optional log compressions (0 = no compression)
        normalize: L^2 normalization if True
        tuning: adjust tuning of chromagram, in units of semitones.
    """

    assert(type(normalize) == bool)
    assert(type(gamma) == int or type(gamma) == float)

    c_fp = spec_to_pitch_fb(fs, fft_len, 'hann', tuning)
    c_pc = np.tile(np.identity(12), 11)[:, 0:128]
    spec = stft_mag(x, fft_len, hop_size)
    
    chroma = np.dot(np.dot(c_pc, c_fp), spec ** 2)
    if gamma > 0:
        chroma = np.log(1 + gamma * chroma)
        
    if normalize:
        # normalize, but only if length > 0 (to avoid div/0 error)
        length = np.linalg.norm(chroma, axis=0, ord = 2)
        valid = length > 0
        chroma[:,valid] /= length[valid]
    return chroma


def cens(chroma, filt_len, ds_rate) :
    """start with a vanilla, un-normalized chromagram.
    1. Apply Manhattan norm
    2. Quantize
    3. Hann window smoothing
    4. downsample
    5. Euclidean norm
    """

    # normalize by L1 norm
    length = np.linalg.norm(chroma, axis=0, ord = 1)
    # handle case where entire feature vector is all zeros:
    zeros = length == 0
    chroma[:,zeros] = 1
    length[zeros] = 12
    chroma = chroma / length

    # quantize according to logarithmic scheme. Resulting values span [0:5]
    quant  = np.zeros(chroma.shape, dtype = np.float)
    values = [1, 2, 3, 4]
    threshs = [0.05, .1, .2, .4, 1]
    for i, v in enumerate(values):
        span = np.logical_and(chroma > threshs[i], chroma <= threshs[i+1])
        quant[span] = v

    # create a smoothing window and filter.
    win = np.hanning(filt_len)
    win = np.atleast_2d(win)
    chroma = scipy.signal.convolve2d(quant, win, mode='same')

    # downsample
    chroma = chroma[:,::ds_rate]

    # normalize again by L2 norm
    length = np.linalg.norm(chroma, axis=0, ord = 2)
    chroma = chroma / length

    return chroma


def spec_to_pitch_fb(fs, fft_len, type = 'box', tuning = 0.) :
    """
    create a conversion matrix (filter bank) from a FT vector to a midi-pitch vector
    aka, log-frequency spectrum 

    type: box = straight box window around frequency range
          tri = triangular window around frequency range
          hann = hanning window around frequency range
    """

    num_bins = fft_len // 2 + 1
    out = np.zeros((128, num_bins))

    # frequncies for each bin in the fft
    bin_f = bin_freqs(fs, fft_len)

    # frequency ranges for each pitch in 0-128. Range is pitch_f[p] to pitch_f[p+1]
    pitch_center = pitch_freqs(0.+tuning, 128.+tuning) 
    pitch_edges  = pitch_freqs(-0.5+tuning, 128.5+tuning) 

    # create a triangular function (f1, 0) -> (f2, 1) -> (f3, 0)
    if type == 'box':
        def _func(f1, f2, f3, x) :
            return np.interp(x, (f1, f3), (1, 1), left = 0, right = 0)

    elif type == 'tri':
        def _func(f1, f2, f3, x) :
            return np.interp(x, (f1, f2, f3), (0, 1, 0))

    elif type == 'hann':
        def _func(f1, f2, f3, x) :
            f = np.linspace(f1, f3, 128)
            h = np.hanning(128)
            return np.interp(x, f, h)

    for p in range(128) :
        out[p:] = _func(pitch_edges[p], pitch_center[p], pitch_edges[p+1], bin_f)

    return out


kTRT = 2**(1/12.)
def pitch_to_freq(p) :
    "Convert midi pitch value to frequency assuming A440 = 69"
    return 440 * (kTRT ** (p - 69.))

def freq_to_pitch(f) :
    "Convert frequency to (floating point) midi pitch assuming A440 = 69"
    return 12 * np.log2(f/440.) + 69

def bin_freqs(fs, fft_len):
    "Return the center frequency of each bin in the FFT"
    return np.arange(fft_len / 2. + 1) * fs / fft_len

def bin_pitches(fs, fft_len):
    "Return the (floating point) midi-pitch value for each FFT bin"
    return freq_to_pitch(bin_freqs(fs, fft_len))

def pitch_freqs(start_pitch = 0, end_pitch = 128) :
    "return the center frequency for each MIDI pitch in the ranage [start_pitch:end_pitch]"
    p = np.arange(start_pitch, end_pitch)
    return pitch_to_freq(p)

def bins_of_pitch(p, fs, fft_len) :
    "returns the list of bins that fall within +/- .5 of pitch p"
    f0 = pitch_to_freq(p-0.5)
    f1 = pitch_to_freq(p+0.5)
    kf = bin_freqs(fs, fft_len)
    
    return [k for k,f in enumerate(kf) if f0 <= f and f < f1]

def stft_mag(x, win_len, hop_size, zp_factor = 1) :
    'returns the magnitude of Short-Time-Fourier-Transform'
    return abs(stft(x, win_len, hop_size, zp_factor))


def stft(x, win_len, hop_size, zp_factor = 1, window = None, centered=True) :
    """
    Return the Short-Time-Fourier-Transform.

    Inputs:
    x: the signal. Assumed real-valued only.
    win_len: the size of the window.
    hop_size: the hop size (H) for the stft
    zp_factor: zero-pad factor. win_len * zp_factor = fft_len
    window: if None, use Hann window, else, use this as the window

    Outputs:
    Return a matrix of shape [num_bins, num_hops]
    where num_bins = win_len /2 + 1 and num_hops is the total # of hops that "fit" into x.

    """

    if window is None:
        window = np.hanning(win_len)
    else:
        win_len = len(window)
    num_bins = (zp_factor * win_len) // 2 + 1

    # zero-pad beginning of x to make centered windows:
    if centered:
        x = np.concatenate((np.zeros(win_len // 2), x))

    num_hops = int( np.ceil(len(x) / hop_size) )

    # zero-pad end of window as needed:
    new_x_len = (num_hops - 1) * hop_size + win_len
    if new_x_len > len(x):
        x = np.concatenate((x, np.zeros(new_x_len - len(x)) ))

    output = np.empty((num_bins, num_hops), dtype = np.complex)

    for h in range(num_hops):
        start = h * hop_size
        end = start + win_len
        sig = x[start:end] * window

        # zero pad 
        if zp_factor > 1:
            sig = np.pad(sig, (0, win_len * (zp_factor - 1)), 'constant')

        # take real FFT
        output[: , h] = np.fft.rfft(sig)

    return output

def make_cost_matrix(x, y):
    '''calculate the cost matrix of two feature vectors x & y using the cosine distance.
       Assumes that x and y are already normalized'''
    cost = 1 - x.T.dot(y)
    return cost

STEPS_TO_TRY = (-1 -1j, -1, -1j)
def simple_steps(C, D, n, m):
    """find least costly way of getting to n,m given cost matrix C and accumulated cost matrix D.
    Returns: 
        the minimal cost,
        the step to get there
    """
    costs = D[n-1,m-1], D[n-1,m], D[n,m-1]
    best  = np.argmin(costs)
    return costs[best] + C[n,m], STEPS_TO_TRY[best]
def simple_steps_w(w):
    """
    Returns a minimal const function with 'w' as the weight to apply to the 
    diagonal step (1,1)
    """
    def f(C, D, n, m):
        costs = D[n-1,m-1] + w * C[n,m], D[n-1,m] + C[n,m], D[n,m-1] + C[n,m]
        best  = np.argmin(costs)
        return costs[best], STEPS_TO_TRY[best]
    return f

def dtw(C, min_cost_func = simple_steps) :
    """finds optimal path from 0,0 to the opposite corner of the cost matrix C.
    the min_cost_func is a function that returns the least costly way of taking one step.

    Returns:
        D: the accumulated cost matrix,
        path: optimal-path
    """

    N, M = C.shape

    # form accumulated cost matrix D:
    D = np.zeros(C.shape)

    # form backtracing matrix to remember steps. Use a complex number
    # to easily (hackily?) store row,column steps where c.real => row, c.imag => column
    S = np.zeros(C.shape, dtype=np.complex)

    # fill in initial values for D:
    # start value
    D[0,0] = C[0,0]
    # column 0 
    for n in range(1,N):
        D[n,0] = C[n,0] + D[n-1,0]
    # row 0
    for m in range(1,M):
        D[0,m] = C[0,m] + D[0,m-1]

    # fill in initial values for S
    S[:,0] = -1
    S[0,:] = -1j

    # compute accumulated cost, and keep track of steps
    for m in range(1,M):
        for n in range(1,N):
            # find minimal cost to reach (n,m). Accumulate into D. Remember step
            cost, step = min_cost_func(C, D, n, m)
            D[n,m] = cost
            S[n,m] = step

    # backtrace to arrive at optimal path
    n = N-1 
    m = M-1
    opt_path = [(n,m)]
    while n > 0 or m > 0:
        step = S[n,m]
        n += int(step.real)
        m += int(step.imag)
        opt_path.append((n,m))

    opt_path.reverse()
    return D, np.array(opt_path)


