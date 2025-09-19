#!/usr/bin/env python3
"""
process_trypo.py
Batch-process trypophobic images:
 - contrast adjustments (factor <1 reduce, >1 increase)
 - mid-frequency boost or suppression in Fourier domain
 - optional phase scramble
 - optional 1/f amplitude replacement

Usage example:
 python process_trypo.py --input_folder trypo_images --output_folder processed \
    --contrast_factors 0.8,1.0,1.5 --mid_freq_boosts 0.5,1.0,2.0 --mid_freq_ranges 8-40 \
    --phase_scramble both
"""

import os
import argparse
import numpy as np
from PIL import Image
import math

def load_image_gray(path, target_size=None):
    img = Image.open(path).convert('L')  # grayscale
    if target_size:
        img = img.resize(target_size, Image.BICUBIC)
    arr = np.array(img, dtype=np.float32) / 255.0
    return arr

def save_image(arr, path):
    arr = np.clip(arr, 0.0, 1.0)
    arr8 = (arr * 255.0).astype(np.uint8)
    Image.fromarray(arr8).save(path)

def rms_contrast(img):
    # standard deviation of luminance; returned relative to mean
    mean = np.mean(img)
    if mean == 0:
        return float(np.std(img))
    return float(np.std(img) / mean)

def adjust_contrast_mean(img, factor):
    # simple contrast change around mean
    m = np.mean(img)
    out = (img - m) * factor + m
    return np.clip(out, 0.0, 1.0)

def get_amp_phase(img):
    F = np.fft.fft2(img)
    Fshift = np.fft.fftshift(F)
    amp = np.abs(Fshift)
    phase = np.angle(Fshift)
    return amp, phase

def reconstruct_from_amp_phase(amp, phase):
    Fshift = amp * np.exp(1j * phase)
    F = np.fft.ifftshift(Fshift)
    img_back = np.fft.ifft2(F)
    img_back = np.real(img_back)
    # normalize to [0,1]
    img_back -= img_back.min()
    if img_back.max() > 0:
        img_back /= img_back.max()
    return img_back

def make_1_over_f(shape):
    h, w = shape
    cy, cx = h//2, w//2
    y = np.arange(h) - cy
    x = np.arange(w) - cx
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    R[cy, cx] = 1.0
    amp = 1.0 / R
    # normalize to mean 1 then scale later
    amp /= np.mean(amp)
    return amp

def manipulate_mid_freq(amp, freq_low, freq_high, boost_factor):
    h, w = amp.shape
    cy, cx = h//2, w//2
    y = np.arange(h) - cy
    x = np.arange(w) - cx
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    mask = (R >= freq_low) & (R <= freq_high)
    out = amp.copy()
    out[mask] = out[mask] * boost_factor
    return out

def parse_list_of_floats(s):
    return [float(x) for x in s.split(',') if x.strip()]

def parse_freq_ranges(s):
    # accepts "8-40" or "8-40;60-80"
    ranges = []
    parts = s.split(';')
    for p in parts:
        if '-' in p:
            a,b = p.split('-')
            ranges.append((int(a), int(b)))
    return ranges

def process_file(path, out_dir, params):
    name = os.path.splitext(os.path.basename(path))[0]
    img = load_image_gray(path, target_size=params.get('resize'))
    orig_amp, orig_phase = get_amp_phase(img)
    mean_amp = np.mean(orig_amp)
    amp_1f = make_1_over_f(img.shape) * mean_amp

    for cf in params['contrast_factors']:
        img_cf = adjust_contrast_mean(img, cf)

        for mf in params['mid_freq_boosts']:
            for freq_range in params['mid_freq_ranges']:
                low, high = freq_range
                base_amp = orig_amp if params['use_original_amp'] else np.abs(np.fft.fftshift(np.fft.fft2(img_cf)))
                new_amp = manipulate_mid_freq(base_amp, low, high, mf)
                if params['use_1_over_f']:
                    amp_to_use = amp_1f
                else:
                    amp_to_use = new_amp

                for phase_mode in params['phase_modes']:
                    if phase_mode == 'scramble':
                        new_phase = np.random.uniform(-np.pi, np.pi, size=orig_phase.shape)
                    else:
                        new_phase = orig_phase

                    recon = reconstruct_from_amp_phase(amp_to_use, new_phase)
                    # final contrast adjustment (to keep consistent)
                    recon = adjust_contrast_mean(recon, cf)

                    out_name = f"{name}_cf{cf}_mf{mf}_f{low}-{high}_{phase_mode}{'_1f' if params['use_1_over_f'] else ''}.png"
                    out_path = os.path.join(out_dir, out_name)
                    save_image(recon, out_path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_folder', required=True)
    parser.add_argument('--output_folder', required=True)
    parser.add_argument('--contrast_factors', default='1.0',
                        help='comma-separated floats, e.g. 0.8,1.0,1.5')
    parser.add_argument('--mid_freq_boosts', default='1.0',
                        help='comma-separated floats (e.g. 0.5,1.0,2.0)')
    parser.add_argument('--mid_freq_ranges', default='8-40',
                        help='freq ranges in pixel units, e.g. 8-40 or 8-40;60-100')
    parser.add_argument('--phase_scramble', choices=['no','yes','both'], default='no',
                        help='phase scramble option')
    parser.add_argument('--use_1_over_f', action='store_true',
                        help='replace amplitude with 1/f amplitude (keep option)')
    parser.add_argument('--use_original_amp', action='store_true',
                        help='use original amplitude as base (default behavior)')
    parser.add_argument('--resize', default=None,
                        help='optional resize: WIDTHxHEIGHT (e.g. 512x512)')

    args = parser.parse_args()

    params = {}
    params['contrast_factors'] = parse_list_of_floats(args.contrast_factors)
    params['mid_freq_boosts'] = parse_list_of_floats(args.mid_freq_boosts)
    params['mid_freq_ranges'] = parse_freq_ranges(args.mid_freq_ranges)
    if args.phase_scramble == 'no':
        params['phase_modes'] = ['orig']
    elif args.phase_scramble == 'yes':
        params['phase_modes'] = ['scramble']
    else:
        params['phase_modes'] = ['orig','scramble']

    params['use_1_over_f'] = args.use_1_over_f
    params['use_original_amp'] = args.use_original_amp

    if args.resize:
        w,h = args.resize.split('x')
        params['resize'] = (int(w), int(h))
    else:
        params['resize'] = None

    os.makedirs(args.output_folder, exist_ok=True)
    files = [f for f in os.listdir(args.input_folder) if f.lower().endswith(('.png','.jpg','.jpeg','.tif','.bmp'))]
    if not files:
        print("No image files found in", args.input_folder)
        return

    for f in files:
        inpath = os.path.join(args.input_folder, f)
        print("Processing", f)
        try:
            process_file(inpath, args.output_folder, params)
        except Exception as e:
            print("Error processing", f, ":", e)

    print("Done. Results in:", args.output_folder)

if __name__ == '__main__':
    main()
