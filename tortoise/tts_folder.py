import argparse
import os
from time import time

import torch
import torchaudio
import shutil

from api import TextToSpeech, MODELS_DIR
from utils.audio import load_audio, load_voices
from utils.text import split_and_recombine_text

def process_folder(input_folder, output_folder, voice, preset, regenerate, candidates, model_dir, seed, produce_debug_state, use_deepspeed, kv_cache, half):
    tts = TextToSpeech(models_dir=model_dir, use_deepspeed=use_deepspeed, kv_cache=kv_cache, half=half)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    complete_folder = input_folder+'\\completed_chapter'

    if not os.path.exists(complete_folder):
        os.makedirs(complete_folder)

    selected_voices = voice.split(',')
    if regenerate is not None:
        regenerate = [int(e) for e in regenerate.split(',')]

    seed = int(time()) if seed is None else seed

    for selected_voice in selected_voices:
        voice_outpath = os.path.join(output_folder, selected_voice)
        os.makedirs(voice_outpath, exist_ok=True)

        if '&' in selected_voice:
            voice_sel = selected_voice.split('&')
        else:
            voice_sel = [selected_voice]

        voice_samples, conditioning_latents = load_voices(voice_sel)
        all_parts = []
        file_count = os.listdir(input_folder).count

        for j, filename in enumerate(os.listdir(input_folder)):
            print(f'Now processing file: {filename}')
            if filename.endswith(".txt"):
                rootname, extension = os.path.splitext(filename)
                input_path = os.path.join(input_folder, filename)
                with open(input_path, 'r', encoding='utf-8') as f:
                    text = ' '.join([l for l in f.readlines()])
                if regenerate is not None and j not in regenerate:
                    all_parts.append(load_audio(os.path.join(voice_outpath, f'{j}.wav'), 24000))
                    continue

                texts = split_and_recombine_text(text)
                
                current_voice_outpath = voice_outpath+'\\'+rootname
                #print(f'saving wav files to: {current_voice_outpath}')
                if not os.path.exists(current_voice_outpath):
                    os.makedirs(current_voice_outpath)
                
                text_outpath = current_voice_outpath+'\\text_files'

                if not os.path.exists(text_outpath):
                    os.makedirs(text_outpath)
                file_num=None
                if os.listdir(text_outpath) == []:
                    for i, text in enumerate(texts):
                        with open(text_outpath+f'\\{rootname}_{i}.txt', 'w', encoding='utf-8') as file: file.write(text)
                else:
                    text_files = os.listdir(text_outpath)
                    
                    print(f'Checking if files exist in {current_voice_outpath}')
                    # wav_files = [f.split(".")[:-1] for f in os.listdir(voice_outpath) if os.path.isfile(f)]
                    wav_files = os.listdir(current_voice_outpath)
                    wav_files.sort()
                    #print(wav_files)
                    wav_name = []
                    for f, file in enumerate(wav_files):
                        if file.endswith(".wav"):
                            print(f'working on {file}')
                            # if os.path.isfile(file):
                            file_name, extension = os.path.splitext(file)
                            #print(file_name)
                            wav_name.append(file_name)
                    # print(wav_name)
                    if not wav_name == []:
                        print(f'There are files. Checking where to continue process')
                       # print(wav_name)
                        for t, text_file in enumerate(text_files):
                            text_name, text_extension = os.path.splitext(text_file)
                            # wav_name = [wave_files.split('.')[0] for x in wave_files]
                            if text_name in wav_name:
                                print(f'{text_file} was already processed.')
                                if file_num == None:
                                    file_num = 0
                                else:
                                    file_num +=1
                                print(f'file_num: {file_num}')


                #print(f'file_num is: {file_num}')
                if file_num == None:
                    file_num = 0
                else:
                    file_num +=1
                #print(f'file_num is now: {file_num}')
                for k, text in enumerate(texts[file_num:], file_num):
                    print(f'Processing text line {k} of {len(texts)} for {filename}')
                    gen = tts.tts_with_preset(text, voice_samples=voice_samples, conditioning_latents=conditioning_latents,
                                              preset=preset, k=candidates, use_deterministic_seed=seed)
                    if candidates == 1:
                        audio_ = gen.squeeze(0).cpu()
                        torchaudio.save(os.path.join(current_voice_outpath, f'{rootname}_{k}.wav'), audio_, 24000)
                        # with open(voice_outpath+'\\'+rootname+f'\\text_files\\{rootname}_{k}.txt', 'w', encoding='utf-8') as file: file.write(text)
                    else:
                        candidate_dir = os.path.join(current_voice_outpath+'\\', str(j))
                        os.makedirs(candidate_dir, exist_ok=True)
                        for c, g in enumerate(gen):
                            torchaudio.save(os.path.join(candidate_dir, f'{rootname}_{k}_{c}.wav'), g.squeeze(0).cpu(), 24000)
                        audio_ = gen[0].squeeze(0).cpu()
                    all_parts.append(audio_)
            
            if os.path.isfile(input_folder+'\\'+filename):
                if filename.endswith(".txt"):
                    shutil.move(input_folder+'\\'+filename, complete_folder+'\\'+filename)
                    print(f"File moved from {input_folder}\\{filename} to {complete_folder}\\{filename}")

        if candidates == 1:
            full_audio = torch.cat(all_parts, dim=-1)
            torchaudio.save(os.path.join(current_voice_outpath, f"combined_{selected_voice}.wav"), full_audio, 24000)

        if produce_debug_state:
            os.makedirs('debug_states', exist_ok=True)
            dbg_state = (seed, texts, voice_samples, conditioning_latents)
            torch.save(dbg_state, f'debug_states/read_debug_{selected_voice}.pth')

        if candidates > 1:
            audio_clips = []
            for candidate in range(candidates):
                for line in range(len(texts)):
                    wav_file = os.path.join(current_voice_outpath, str(line), f"{candidate}.wav")
                    audio_clips.append(load_audio(wav_file, 24000))
                audio_clips = torch.cat(audio_clips, dim=-1)
                torchaudio.save(os.path.join(current_voice_outpath, f"combined_{selected_voice}_{candidate:02d}.wav"), audio_clips, 24000)
                audio_clips = []

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_folder', type=str, help='Folder containing text files to read.', default="input_folder/")
    parser.add_argument('--voice', type=str, help='Selects the voice to use for generation. See options in voices/ directory (and add your own!) '
                                                   'Use the & character to join two voices together. Use a comma to perform inference on multiple voices.', default='pat')
    parser.add_argument('--output_folder', type=str, help='Where to store outputs.', default='output_folder/')
    parser.add_argument('--preset', type=str, help='Which voice preset to use.', default='standard')
    parser.add_argument('--regenerate', type=str, help='Comma-separated list of clip numbers to re-generate, or nothing.', default=None)
    parser.add_argument('--candidates', type=int, help='How many output candidates to produce per-voice. Only the first candidate is actually used in the final product, the others can be used manually.', default=1)
    parser.add_argument('--model_dir', type=str, help='Where to find pretrained model checkpoints. Tortoise automatically downloads these to .models, so this'
                                                      'should only be specified if you have custom checkpoints.', default=MODELS_DIR)
    parser.add_argument('--seed', type=int, help='Random seed which can be used to reproduce results.', default=None)
    parser.add_argument('--produce_debug_state', type=bool, help='Whether or not to produce debug_state.pth, which can aid in reproducing problems. Defaults to true.', default=True)
    parser.add_argument('--use_deepspeed', type=bool, help='Use deepspeed for speed bump.', default=False)
    parser.add_argument('--kv_cache', type=bool, help='If you disable this please wait for a long a time to get the output', default=True)
    parser.add_argument('--half', type=bool, help="float16(half) precision inference if True it's faster and take less vram and ram", default=True)
    parser.add_argument('--reuse_samples', type=bool, help="if set to true, once it does the initial Generating Autoregressive Samples, it will save and reuse on next iteration.", default=False)

    args = parser.parse_args()
    if torch.backends.mps.is_available():
        args.use_deepspeed = False

    process_folder(args.input_folder, args.output_folder, args.voice, args.preset, args.regenerate, args.candidates, args.model_dir, args.seed, args.produce_debug_state, args.use_deepspeed, args.kv_cache, args.half)
