from flask import Flask,jsonify

from flask import Flask, request, jsonify
import os,hashlib,secrets
import threading
from download_function import download_file_with_progress 

def IDGenerator(filedest:str):
    _id=secrets.token_hex(16)
    if _id in Files_inprogress.keys():
        if Files_inprogress[id]==0:# is finished
            del Files_inprogress[id]
            return _id
        else:
            return IDGenerator(filedest)
    return _id

app =Flask(__name__)
Files_inprogress={}#{id:{'dl':Expected size,'filename':'name.txt'} | dl=0 if finished}
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
    Files_inprogress[id]={'dl':filesize,'filename':filename}

    # Use threading to download the file asynchronously
    download_thread =threading.Thread(target=download_file_with_progress, args=(url, destination_path))
    download_thread.start()

    return jsonify({'message':'Download started','filename':filename}), 200

@app.route('/progress/<ActionID>')
def progress(ActionID):
    # Assuming the progress is calculated based on the downloaded file size compared to the expected file size
    try:
        destination_path =f"downloads/{Files_inprogress[ActionID]['filename']}"
    except Exception as ex:
        import logging
        logging.error("Error on selecting file in progress maybe it is finished & removed. Error: "+str(ex))
        return jsonify("Error on selecting file in progress maybe it is finished & removed.")
    if os.path.exists(destination_path):
        expected_file_size=Files_inprogress[Files_inprogress[ActionID]["dl"]]
        if expected_file_size:
            downloaded_file_size=round(float(os.path.getsize(destination_path)/(1024*1024)),2) #convert bytes to MB
            progress_percent =(downloaded_file_size / expected_file_size)*100
            return jsonify({'progress': progress_percent}), 200

    return jsonify({'error':'File not found or progress unavailable'}), 404

@app.route("/finish/<ActionID>",methods=["POST"])
def finish_action(ActionID):
    Files_inprogress[ActionID]=0
@app.route('/selectall')
def selectall():
    return jsonify(Files_inprogress)
app.route('/delete/<actionid>')
def deleting(actionid):
    del Files_inprogress[actionid]

if __name__=='__main__':
    app.run(debug=True)
