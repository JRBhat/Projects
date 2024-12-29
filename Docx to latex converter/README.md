# Python Script for Converting .docx to LaTeX

This Python script converts a Microsoft Word `.docx` file into a LaTeX `.tex` file. The script processes the contents of the Word document, including paragraphs and tables, and generates a LaTeX document ready to be converted into a PDF. The script utilizes the `docx` library to read Word documents, and it employs a graphical user interface (GUI) created using the `gooey` library to allow the user to select the input file.



## Key Features and Functionality

### Document Parsing:
- The script uses `python-docx` to read the contents of a Word document. It retrieves all paragraphs and tables from the document.
- The text is cleaned (e.g., removing empty strings) and organized into structured lists for further processing.

### LaTeX File Generation:
- The script then generates a `.tex` file, wrapping the extracted data in LaTeX syntax.
- The content from paragraphs and tables is written to the LaTeX document, which can later be compiled into a PDF.

### Table Handling:
- The script handles tables in the Word document by extracting text from the table cells and formatting it into LaTeX-style descriptions.
- The tables are treated differently based on their structure, with special handling for the last table (Type B), where additional bullet points are generated.

### Subsections and Headings:
- The script organizes the document into sections and subsections based on the paragraphs, ensuring the structure is maintained in the LaTeX document.
- Special LaTeX commands are used to escape characters that have specific meanings in LaTeX (e.g., `_`, `&`, `%`).

### GUI Integration (Gooey):
- The script uses `gooey` to create a simple GUI that allows the user to select a `.docx` file for processing.
- The GUI enhances the user experience by providing an intuitive file picker.



## Detailed Explanation of the Workflow

### File Selection and Parsing:
1. The user selects a `.docx` file using the Gooey interface.
2. The file is then parsed to extract paragraphs and tables.

### Content Organization:
- Paragraphs are categorized into general sections (with headings and descriptions).
- Tables are processed row by row, and each cell's text is stored in structured lists. Special handling is done for the last table, where additional formatting and bullet points are added.

### LaTeX File Construction:
- The LaTeX file starts with a document class declaration and begins writing the extracted sections and tables.
- For each section and table, LaTeX commands are used to format headings, paragraphs, and lists correctly.

### Output:
- The script generates a `.tex` file in the same folder as the input `.docx` file.
- The LaTeX file can be compiled using a LaTeX editor (e.g., Overleaf, TeXShop) to produce a formatted PDF.
