import os
import torchaudio
import torch
import argparse

def merge_wav_files(input_folder, output_folder, target_sample_rate=None):
    # List all WAV files in the input folder
    wav_files = [f for f in os.listdir(input_folder) if f.endswith('.wav')]

    if not wav_files:
        print("No WAV files found in the input folder.")
        return

    # Create a dictionary to store merged waveforms by prefix
    merged_waveforms = {}

    for wav_file in wav_files:
        file_path = os.path.join(input_folder, wav_file)
        prefix = wav_file.split('_')[0]  # Assuming underscore '_' is the separator

        # Load the waveform
        wave, sr = torchaudio.load(file_path)

        if target_sample_rate and sr != target_sample_rate:
            # Resample the waveform to the target sample rate
            resampler = torchaudio.transforms.Resample(sr, target_sample_rate)
            wave = resampler(wave)

        if prefix not in merged_waveforms:
            merged_waveforms[prefix] = {
                "waveform": wave,
                "sample_rate": target_sample_rate or sr
            }
        else:
            # Check if sample rates match
            if target_sample_rate and sr != target_sample_rate:
                print(f"Warning: Sample rates do not match for file {wav_file}. Skipping.")
                continue

            # Concatenate the waveform
            merged_waveforms[prefix]["waveform"] = torch.cat((merged_waveforms[prefix]["waveform"], wave), dim=1)

    # Save merged waveforms to separate files by prefix
    for prefix, data in merged_waveforms.items():
        output_file = os.path.join(output_folder, f"{prefix}_merged.wav")
        torchaudio.save(output_file, data["waveform"], data["sample_rate"])
        print(f"Merged WAV files with prefix '{prefix}' and saved to '{output_file}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge and save WAV files by prefix.")
    parser.add_argument("input_folder", type=str, help="Path to the input folder containing WAV files.")
    parser.add_argument("output_folder", type=str, help="Path to the output folder where merged WAV files will be saved.")
    parser.add_argument("--target_sample_rate", type=int, default=None, help="Target sample rate for resampling.")
    args = parser.parse_args()
    
    input_folder = args.input_folder
    output_folder = args.output_folder
    target_sample_rate = args.target_sample_rate
    
    merge_wav_files(input_folder, output_folder, target_sample_rate)
