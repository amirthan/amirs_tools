import os
from fpdf import FPDF

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
INCLUDE_EXTENSIONS = ['.py', '.cpp', '.c', '.html', '.css','.js']

class PDFWithTOC(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.toc = []
        self.current_page = 1

    def header(self):
        self.set_font('Arial', 'B', 12)
        if self.page_no() == 1:
            self.cell(0, 10, 'Repository Code Structure', 0, 1, 'C')
        else:
            self.cell(0, 10, f'Page {self.page_no()}', 0, 1, 'C')

    def add_section(self, title, content):
        self.add_page()
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1)
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 10, content)
        self.toc.append((title, self.page_no()))

    def add_toc(self):
        self.add_page()
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Table of Contents', 0, 1, 'C')
        self.set_font('Arial', '', 12)
        for title, page in self.toc:
            self.cell(0, 10, f'{title} ..... {page}', 0, 1)
        self.current_page = self.page_no()

def should_process_file(file_path):
    if os.path.getsize(file_path) > MAX_FILE_SIZE:
        print(f"Skipping {file_path}: exceeds max file size")
        return False
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in INCLUDE_EXTENSIONS:
        return False
    return True

def process_directory_for_pdf(pdf, path, root_len):
    counter = 1
    for root, _, files in os.walk(path):
        relative_root = root[root_len:]
        for file in sorted(files):
            file_path = os.path.join(root, file)
            if not should_process_file(file_path):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

            title = f"{counter}. {os.path.join(relative_root, file)}"
            pdf.add_section(title, content)
            counter += 1

def main(repository_path):
    pdf = PDFWithTOC()
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    # First pass to build TOC entries
    process_directory_for_pdf(pdf, repository_path, len(repository_path))
    # Add TOC at the beginning
    pdf.add_toc()
    
    # Expand the user's home directory in the output path
    output_path = os.path.expanduser(os.path.join(repository_path, "repository_code_structure.pdf"))
    pdf.output(output_path)
    print(f"PDF generated: {output_path}")

if __name__ == "__main__":
    # Expand the user's home directory in the input path
    repo_path = os.path.expanduser(input("Enter the repository path: ").strip())
    main(repo_path)
