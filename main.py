import os
import requests
import re
from PIL import Image
from io import BytesIO
import time
from PyPDF2 import PdfMerger

# Function to create directories if they don't exist
def create_directories():
    os.makedirs("saved-temp", exist_ok=True)
    os.makedirs("saved-exported", exist_ok=True)
    print("Directories 'saved-temp' and 'saved-exported' are ready.")

# Function to download and save images with retries
def download_images_from_url(url, page_number, max_retries=10, wait_time=2):
    print(f"Processing URL: {url}")

    for attempt in range(max_retries):
        time.sleep(wait_time)
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve page {page_number}. HTTP status code: {response.status_code}. Retrying in {wait_time} seconds ... (Attempt {attempt +1} of {max_retries}")
        # Find all base64 image data using the class "pdf"

        if response:
            image_path = f"saved-temp/{page_number}.pdf"
            with open(image_path, 'wb') as img_file:
                img_file.write(response.content)
            print(f"Saved pdf {page_number}.pdf")
            break
        else:
            if attempt < max_retries - 1:
                print(f"No images found on page {page_number}. Retrying in {wait_time} seconds... (Attempt {attempt + 1} of {max_retries})")
            else:
                print(f"Failed to find images on page {page_number} after {max_retries} attempts.")

# Function to convert saved images to a PDF
def merge_pdfs(creditID):
    pdf_path = f"saved-exported/exported{creditID}.pdf"
    images = []
    image_files = sorted([f for f in os.listdir("saved-temp") if f.endswith('.pdf')], key=lambda x: int(re.sub('\D', '', x)))


    print("Merging...")

    merger = PdfMerger()

    if image_files:
        print("No images found to convert to PDF.")

    for pdf in image_files:
        merger.append(f"saved-temp/{pdf}")


    with open(pdf_path, 'wb') as output_file:
        merger.write(output_file)
    print(f"PDF saved as {pdf_path}")

def open_path(p):
    if not os.path.exists(p): raise FileNotFoundError(p)
    if os.name == 'nt':
        os.startfile(p)
        return
    q = "'" + p.replace("'", "'\\''") + "'"
    cmd = ('open ' if os.popen('uname').read().strip() == 'Darwin' else 'xdg-open ') + q
    if os.system(cmd): raise RuntimeError(cmd)

# Main script execution
def main():
    create_directories()

    # Input the base URL, first, and last page numbers
    creditID = input("ID from URL https://api-folio.rokus-klett.si/v1/pdf/______/: ")
    base_url = f"https://api-folio.rokus-klett.si/v1/pdf/{creditID}/"
    metadata = requests.get(f"https://api-folio.rokus-klett.si/v1/metadata/{creditID}")
    if metadata.status_code != 200:
        print(f"Failed to retrieve metadata. HTTP status code: {response.status_code}.")
    metadata = metadata.json()
    last_page = metadata["pageCount"]
    print(f"Detected {last_page} pages from metadata.")
    # Use hardcoded token
    if metadata["loginRequired"] == True:
        token = input("Token: ")
    # Generate page ranges and download images
    for current_page in range(178, last_page):
        url = f"{base_url}{current_page}?token={token}"
        download_images_from_url(url, current_page)

    merge_pdfs(creditID)

    # Ask user if they want to delete the temporary directory
    delete_temp = input("Do you want to delete the temp directory 'saved-temp'? (y/n): ").strip().lower()

    try:
        if delete_temp == 'y':
            for image_file in os.listdir("saved-temp"):
                os.remove(os.path.join("saved-temp", image_file))
            os.rmdir("saved-temp")
            print("Temporary directory 'saved-temp' deleted.")
    except:
        print("The temp directory may not have been deleted...")

    # Open the PDF
    print("Opening the PDF...")
    open_path(f"saved-exported/exported{creditID}.pdf")

    print("Process completed successfully.")

if __name__ == "__main__":
    main()
