from cpq_parser import parse_input
import sys


if __name__ == "__main__":
    # Check if a filename is provided as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: cpq.py <filename>.ou")
        sys.exit(1)

    # Get the filename from command-line argument
    file_path = sys.argv[1]


    # Check if the extensions of the file is .ou
    if not file_path.endswith('.ou'):
        print("Error: The file extension must be .ou")
        sys.exit(1)
    file_name=file_path[:-3]
    
    # Open the file for reading
    with open(file_path, "r") as file:
        content = file.read()
        ast = parse_input(content)
        try:
            quad = ast.code_gen()
            with open(f'{file_name}.qud', 'w') as file:
                file.write(quad)
                file.write('Yahel Megidish')
                sys.stderr.write('Yahel Megidish')

        except:
            sys.stderr.write('\nError could not create output file.')

