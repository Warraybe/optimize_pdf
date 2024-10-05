# optimize_pdf
Python script to optimize PDFs with a recursive search of folders

## Usage
Simply place the optimize.py file in a folder and run. It will scan the folder, and sub-folders for PDFs. If found, it will process the files and reduce image quality to 75%, compress pages, and remove duplicated items using references instead. The script use threads and will process a folder completely before moving onto the next.
