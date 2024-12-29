from gooey import Gooey, GooeyParser
from parser import parse_document
from latex_writer import generate_latex_document
from utils import clean_list

@Gooey
def main():
    """
    This function generates a GUI allowing the user to input the path of the target file.
    It parses the Word document and generates a LaTeX document.
    """
    # Set up Gooey parser for GUI-based input
    parser = GooeyParser(description="DocToLatex converter")
    parser.add_argument(
        "doc_file", help="The file you want to process", type=str, widget="FileChooser"
    )
    args = parser.parse_args()
    doc_filename = args.doc_file

    # Parse the document into structured content
    content = parse_document(doc_filename)
    
    # Generate the LaTeX file
    tex_filename = generate_latex_document(content, doc_filename)

    print(f"File generated: {tex_filename}")


if __name__ == "__main__":
    main()
