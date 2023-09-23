import argparse
import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re

def convert_epub_to_txt(epub_file):
    # Check if the file is an EPUB
    if not epub_file.lower().endswith('.epub'):
        print("Not an EPUB file. Please provide an EPUB file.")
        return None

    book = epub.read_epub(epub_file)
    content = []

    # Extract content from EPUB
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            # Decode bytes to string using UTF-8 encoding
            content.append(item.content.decode('utf-8'))

    # Combine HTML content and remove tags
    combined_content = ' '.join(content)
    soup = BeautifulSoup(combined_content, 'html.parser')
    text = soup.get_text()

    return text


def prepare_text(text):
    # Remove hyphens
    text = text.replace('-', ' ')

    # Replace left and right single quotes with straight single quotes
    text = text.replace('‘', "'").replace('’', "'")

    # Split the text into lines and remove empty lines
    lines = [line.rstrip() for line in text.split('\n') if line.strip()]

    new_lines = []

    is_chapter = False  # Flag to track if the previous line was a chapter title

    for line in lines:
        # Check if the line is a lone number on its own line
        if re.match(r'^\d+$', line):
            # Prefix with 'Chapter' and add '... ' only once after it
            if not is_chapter:
                line = 'Chapter ' + line + '... '
                is_chapter = True
        else:
            is_chapter = False

        new_lines.append(line)

    # Join the lines back together
    text = '\n'.join(new_lines)

    # Ensure clear chapter sections
    text = re.sub(r'CHAPTER \d+', lambda x: x.group().lower(), text)

    return text

def add_pipe_to_text(text, max_chars=200):
    # Split the text into words
    words = text.split()

    new_text = ""
    char_count = 0

    for word in words:
        # Check if adding the current word exceeds the maximum character count
        if char_count + len(word) + 1 > max_chars:  # +1 for the space
            new_text += " | "  # Add a pipe and space
            char_count = 0  # Reset the character count

        if new_text:
            new_text += " "  # Add a space before the word if it's not the first word
            char_count += 1  # Add 1 for the space

        new_text += word
        char_count += len(word)

    return new_text

def add_newline_before_and_after_chapter(text):
    # Use a regular expression to find 'Chapter' followed by a space and a digit
    # and add a newline character '\n' before and after it, including 'Chapter' in both lines.
    text = re.sub(r'((Chapter|Prologue|Epilogue) \d+\.\.\.(\s)?)', r'\n\n\1\n\n', text)
    text = re.sub(r'((Prologue|Epilogue)\.\.\.(\s)?)', r'\n\n\1\n\n', text)
    
    return text


def main():
    parser = argparse.ArgumentParser(description="Prepare a text file for TTS conversion.")
    parser.add_argument("input_file", type=str, help="Path to the input EPUB or TXT file.")
    parser.add_argument("-o", "--output_file", type=str, help="Path to the output TXT file. Defaults to the input location.")
    parser.add_argument("--add_pipe", action="store_true", default=False, help="Add a '|' after each sentence")
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file

    # If the input is an EPUB, convert it to TXT
    if input_file.lower().endswith('.epub'):
        text = convert_epub_to_txt(input_file)
    elif input_file.lower().endswith('.txt'):
        # If it's already a TXT file, read it
        with open(input_file, 'r', encoding='utf-8') as file:
            text = file.read()
    else:
        print("Unsupported file format. Please provide an EPUB or TXT file.")
        return

    # Prepare the text
    text = prepare_text(text)
    if args.add_pipe:
        # add pipe to text
        text = add_pipe_to_text(text, 200)
    text = add_newline_before_and_after_chapter(text)

    # Determine the output file path
    if output_file is None:
        # If no output file is specified, use the same location as the input file with a .txt extension
        base_name, _ = os.path.splitext(input_file)
        output_file = base_name + "_prepared.txt"

    # Write the prepared text to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(text)

    print(f"Text prepared and saved to {output_file}")

if __name__ == "__main__":
    main()
