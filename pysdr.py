import numpy as np
import asciichartpy
import rtlsdr
import os
import sys
import select

# RTL-SDR settings# Starting frequency in Hz
sample_rate = 2.4e6  # Sample rate in Hz
num_samples = 1024  # Number of samples to capture per sweep

# Frequency range to sweep
start_freq = 24e6  
center_freq = start_freq  # Start frequency in Hz
end_freq = 600e6  # End frequency in Hz
step_freq = 12.125e6  # Frequency step size in Hz
start_mhz = start_freq / 1e6
end_mhz = end_freq / 1e6

# Calculate the number of sweeps
num_sweeps = int((end_freq - start_freq) / step_freq) + 1

# Initialize RTL-SDR
sdr = rtlsdr.RtlSdr()
sdr.sample_rate = sample_rate
sdr.center_freq = center_freq

def generate_ascii_chart(data, height=15):
    freqs, strengths = zip(*data)
    max_strength = max(strengths)
    normalized_strengths = [s / max_strength for s in strengths]
    chart = ""
    for i in range(height, 0, -1):
        line = ""
        for val in normalized_strengths:
            if val >= i / height:
                line += "|"
            else:
                line += " "
        chart += line + "\n"
    return chart

def format_frequency(freq):
    return f"{freq/1e6:.3f}"  # Convert to MHz and format to 3 decimal places

# Calculate the frequency step size in MHz
freq_step = step_freq / 1e6

while True:
    frequencies = []
    signal_strengths = []

    for i in range(num_sweeps):
        freq = start_freq + i * step_freq
        sdr.center_freq = freq
        samples = sdr.read_samples(num_samples)

        # Calculate signal strength
        signal_strength = np.abs(samples).mean()

        # Store frequency and signal strength
        frequencies.append(freq)
        signal_strengths.append(signal_strength)

    # Prepare data for ASCII chart
    data = list(zip(frequencies, signal_strengths))

    # Generate ASCII chart with reduced height
    chart = generate_ascii_chart(data, height=8)
    os.system('cls' if os.name == 'nt' else 'clear')

    print("                                 py-sdr")
    print("""
██████╗ ██╗   ██╗     ███████╗██████╗ ██████╗ 
██╔══██╗╚██╗ ██╔╝     ██╔════╝██╔══██╗██╔══██╗
██████╔╝ ╚████╔╝█████╗███████╗██║  ██║██████╔╝
██╔═══╝   ╚██╔╝ ╚════╝╚════██║██║  ██║██╔══██╗
██║        ██║        ███████║██████╔╝██║  ██║
╚═╝        ╚═╝        ╚══════╝╚═════╝ ╚═╝  ╚═╝
    x421 2023
    """)
    print(f"~{freq_step:.2f} MHz" + " " * 10 + f"~{freq_step * 10:.2f} MHz") 
    print(chart)
    header_line = f"|{start_mhz:.2f}Mhz{'_' * (int((end_mhz - start_mhz) // freq_step) - 30)}{end_mhz:.2f}Mhz_|"
    print(header_line)
    # Find peak signal strengths and corresponding frequencies
    peak_indices = np.argsort(signal_strengths)[::-1][:3]
    peak_frequencies = [frequencies[i] for i in peak_indices]
    peak_strengths = [signal_strengths[i] for i in peak_indices]
    print("| Rank |  Frequency (MHz)  |   Strength   |")
    print("|------+-------------------+--------------|")
    for i, (freq, strength) in enumerate(zip(peak_frequencies, peak_strengths)):
        print(f"|  {i+1:<4}|  {format_frequency(freq):<17}|  {strength:>8.2f}    |")
    print("|------+-------------------+--------------|")


    print("Press 'q' to quit or any other key to continue...")
    user_input, _, _ = select.select([sys.stdin], [], [], 0)
    if user_input:
        char = sys.stdin.read(1)
        if char.lower() == 'q':
            sdr.close()
            sys.exit() 
        sdr.close()
        
sdr.close()

