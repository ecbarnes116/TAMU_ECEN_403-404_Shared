import pandas as pd
sampling_rate = 2000

def analyze_signal(signal, time):
    max_val = np.max(signal)
    min_val = np.min(signal)
    avg_val = np.mean(signal)
    max_time = time[np.argmax(signal)]
    min_time = time[np.argmin(signal)]

    fft_vals = np.fft.fft(signal)
    frequencies = np.fft.fftfreq(len(signal), d=1 / sampling_rate)

    positive_freq_idxs = np.where(frequencies > 0)
    fft_vals = fft_vals[positive_freq_idxs]
    frequencies = frequencies[positive_freq_idxs]
    max_fft_magnitude = np.max(np.abs(fft_vals))
    freq_at_max_magnitude = frequencies[np.argmax(np.abs(fft_vals))]

    dominant_freq = frequencies[np.argmax(np.abs(fft_vals[1:])) + 1]

    a = {
        "max_val": round(max_val,3), #图片上显示的Max(显示)
        "min_val": round(min_val,3), #图片上显示的Min(显示)
        "avg_val": round(avg_val,3), #图片上显示的Avg(显示)
        "max_time": max_time, #max_val对应的时间(不显示在图片上但是需要数值)
        "min_time": min_time, #min_val对应的时间(不显示在图片上但是需要数值)
        "dominant_freq": round(dominant_freq,3),#图片上显示的Frequency(显示)
        "fft_vals": fft_vals, #不显示在图片上但是需要数值
        "frequencies": frequencies, #不显示在图片上但是需要数值
        "max_fft_magnitude": round(max_fft_magnitude,3), #图片上显示的Max FFT Amp(显示)
        "freq_at_max_magnitude": freq_at_max_magnitude #不显示在图片上但是需要数值
    }
    for k,v in a.items():
        print(k,v)
    return a


# shape的code，把这个结果显示到Shape那块就可以了
import numpy as np
from scipy.signal import find_peaks

def shape(x):
    # Generate a sample wave-like data
    # x = np.linspace(0, 10 * np.pi, 500)
    y = np.tan(x)
    # Find peaks
    peaks, _ = find_peaks(y, distance=20)
    # Check shape
    if len(peaks) > 1:
        shape = "wave"
    else:
        shape = "unknown"
    return shape


if __name__ == '__main__':
    # print(shape())
    data = pd.read_csv("./random_signal99.csv")
    res = analyze_signal(data['amplitude 1'], data['time'])
    for k,v in res.items():
        print(k,v)