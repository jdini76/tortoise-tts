import os

def parse_and_save_files(input_filename, keyword):
    try:
        with open(input_filename, 'r', encoding='utf-8') as input_file:
            content = input_file.read()

            sections = content.split(keyword)

            # Create a directory with the keyword as its name
            output_dir = f"{keyword}_output"
            os.makedirs(output_dir, exist_ok=True)
            
            for i, section in enumerate(sections):
                i = "{:02d}".format(i)
                output_filename = os.path.join(output_dir, f"{keyword}_{i}.txt")
                with open(output_filename, 'w', encoding='utf-8') as output_file:
                    # Include the keyword with the text in the output file
                    output_file.write(f"{keyword}{section}")
                print(f"Created {output_filename}")

        print("Parsing and saving completed.")

    except FileNotFoundError:
        print(f"Error: File '{input_filename}' not found.")

if __name__ == "__main__":
    input_filename = input("Enter the input text file name: ")
    keyword = input("Enter the keyword for splitting: ")
    parse_and_save_files(input_filename, keyword)
