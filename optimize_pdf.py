import logging
import os
import threading

import pypdf

thread_count = 0
thread_count_lock = threading.Lock()
logger = logging.getLogger("pypdf")
logger.setLevel(logging.ERROR)


def optimize_pdf(input_file: str, output_file: str) -> None:
    """Optimizes PDF by reducing image quality, compressing pages, and removing duplicates.

    Args:
        input_file (str): The file name for the PDF to optimize.
        output_file (str): The output file name for the optimized pdf.
    """
    global thread_count
    initial_size: int = os.path.getsize(input_file)

    # Open the input PDF file
    with open(input_file, "rb") as input:
        with thread_count_lock:
            thread_count += 1

        # Create a new PDF reader object
        pdf_reader = pypdf.PdfReader(input)

        # Create a new PDF writer object
        pdf_writer = pypdf.PdfWriter()

        # Iterate through the pages of the input PDF
        for page_number, page in enumerate(pdf_reader.pages):
            # Add page to writer
            pdf_writer.add_page(page)
            # Get page to adjust images
            write_page: pypdf.PageObject = pdf_writer.pages[page_number]

            for img in write_page.images:
                # Reduce image quality on page
                img.replace(img.image, quality=75)

            # Compress page
            write_page.compress_content_streams()

        # Remove duplication
        pdf_writer.compress_identical_objects()

    # Write the optimized PDF to the output file
    with open(output_file, "wb") as output:
        pdf_writer.write(output)
        optimized_size: int = os.path.getsize(output_file)

    if optimized_size < initial_size:
        os.remove(input_file)
        os.rename(output_file, input_file)
        print(
            f"Compressed to {optimized_size / initial_size:.2%} of file size: {os.path.split(input_file)[1]}"
        )
    else:
        os.remove(output_file)
        print(f"Already compressed: {os.path.split(input_file)[1]}")

    with thread_count_lock:
        thread_count -= 1
        print(f"Files left: {thread_count}")


def scan_folder(folder_path: str) -> None:
    """
    Scans a folder and its subfolders for PDF files and optimizes them.

    Args:
        folder_path (str): The path to the folder to be scanned.
    """
    threads: list = []
    for dir_name, sub_dirs, file_list in os.walk(folder_path):
        for file in file_list:
            if file.endswith(".pdf"):
                input_file: str = os.path.join(dir_name, file)
                output_file: str = os.path.join(dir_name, f"optimized_{file}")
                thread = threading.Thread(
                    target=optimize_pdf, args=(input_file, output_file)
                )
                thread.start()
                threads.append(thread)

        # Wait for all threads to clear before moving into next directory
        if threads:
            # Print current thread count and working directory
            current_dir: str = os.path.relpath(dir_name, folder_path)
            print(f"{len(threads)} files in folder: {current_dir}")
            for thread in threads:
                thread.join()
            # Print folder name on folder completion
            print(f"Folder {current_dir} complete.")
        threads.clear()


# Get the current directory
current_dir: str = os.getcwd()

# Scan the current directory and its subfolders for PDF files
scan_folder(current_dir)
