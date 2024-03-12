import requests
from tqdm import tqdm  

def download_file_with_progress(url, destination,chunksize=8192):
    try:
        response = requests.head(url)
        response.raise_for_status()

        content_length = response.headers.get('Content-Length')
        if content_length is None:
            print("Cannot determine file size. Proceeding with download.")
        else:
            file_size = int(content_length)
            print(f"File size: {file_size / (1024 * 1024):.2f} MB")

        # Perform the actual download with tqdm progress bar
        with requests.get(url, stream=True) as response:
            response.raise_for_status()

            with open(destination, 'wb') as file, tqdm(
                desc="Downloading",
                total=file_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=chunksize):
                    file.write(chunk)
                    progress_bar.update(len(chunk))

        print(f"File downloaded successfully to {destination}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading the file: {e}")

# Example usage
url = "https://example.com/sample_file.zip"
destination_path = "path/to/save/sample_file.zip"
download_file_with_progress(url, destination_path)
