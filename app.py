from flask import Flask,jsonify

from flask import Flask, request, jsonify
import os,hashlib,secrets
import threading
from download_function import download_file_with_progress 

def IDGenerator(filedest:str):
    return secrets.token_hex(16)

app =Flask(__name__)
Files_inprogress={}
@app.route('/download', methods=['POST'])
def download():
    """sample of json input {'url':'http://sample.com','filesize':'100'} filesize must be in MB"""
    url=request.json.get('url')
    filesize=request.json.get('filesize')
    if not url:
        return jsonify({'error': 'URL not provided'}), 400
    filename =os.path.basename(url)
    destination_path =f"downloads/{filename}"
    id=IDGenerator(destination_path)
    if id in Files_inprogress.keys():
        if 

    Files_inprogress[id]=filesize

    # Use threading to download the file asynchronously
    download_thread =threading.Thread(target=download_file_with_progress, args=(url, destination_path))
    download_thread.start()

    return jsonify({'message':'Download started','filename':filename}), 200

@app.route('/progress/<filename>')
def progress(filename):
    # Assuming the progress is calculated based on the downloaded file size compared to the expected file size
    destination_path =f"downloads/{filename}"
    if os.path.exists(destination_path):
        expected_file_size=Files_inprogress[]
        if expected_file_size:
            downloaded_file_size=os.path.getsize(destination_path)//(1024*1024) #convert bytes to MB
            progress_percent =(downloaded_file_size / expected_file_size)*100
            return jsonify({'progress': progress_percent}), 200

    return jsonify({'error':'File not found or progress unavailable'}), 404

if __name__=='__main__':
    app.run(debug=True)
