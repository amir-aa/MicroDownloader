from flask import Flask,jsonify
from flask import Flask, request, jsonify
import os,hashlib,secrets
import threading,logging
from download_function import download_file_with_progress ,download_file_with_progress_limited

def IDGenerator(filedest:str):
    _id=secrets.token_hex(16)
    if _id in Files_inprogress.keys():
        if Files_inprogress[_id]["dl"]==0:# is finished
            del Files_inprogress[_id]
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
    chunksize=request.json.get('chunksize')
    if not chunksize:
        chunksize=8192
    if not url:
        return jsonify({'error': 'URL not provided'}), 400
    filename =os.path.basename(url)
    destination_path =f"downloads/{filename}"
    id=IDGenerator(destination_path)
    Files_inprogress[id]={'dl':filesize,'filename':filename}

    #threading to download the file asynchronously
    download_thread =threading.Thread(target=download_file_with_progress, args=(url,destination_path,id,int(chunksize)))
    download_thread.start()
    #Files_inprogress[id]["tr"]=download_thread

    return jsonify({'message':'Download started','filename':filename,"ActionID":id}), 200

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
        expected_file_size=Files_inprogress[ActionID]["dl"]
        if expected_file_size:
            if expected_file_size==0:
                return jsonify({'progress': "100"})
            downloaded_file_size=round(float(os.path.getsize(destination_path)/(1024*1024)),2) #convert bytes to MB
            progress_percent =(downloaded_file_size / expected_file_size)*100
            return jsonify({'progress': progress_percent}), 200

    return jsonify({'error':'File not found or progress unavailable'}), 404

@app.route("/finish/<ActionID>",methods=["POST"])
def finish_action(ActionID):
    Files_inprogress[ActionID]["dl"]=0#we make it zero because the File might be deleted
    print("finished registered",ActionID)
    return jsonify("finished registered "+str(ActionID))
@app.route('/selectall')
def selectall():
    return jsonify(Files_inprogress)
@app.route('/delete/<actionid>')
def deleting(actionid):
    del Files_inprogress[actionid]

@app.route('/limitdownload', methods=['POST'])
def _download():
    """sample of json input {'url':'http://sample.com','filesize':'100'} filesize must be in MB"""
    url=request.json.get('url')
    filesize=request.json.get('filesize')
    chunksize=request.json.get('chunksize')
    if not chunksize:
        chunksize=8192
    if not url:
        return jsonify({'error': 'URL not provided'}), 400
    try:
        filename =os.path.basename(url)
        destination_path =f"downloads/{filename}"
        id=IDGenerator(destination_path)
        Files_inprogress[id]={'dl':filesize,'filename':filename}

        #threading to download the file asynchronously
        download_thread =threading.Thread(target=download_file_with_progress, args=(url,destination_path,id,int(chunksize)))
        download_thread.start()
        #Files_inprogress[id]["tr"]=download_thread

        return jsonify({'message':'Download started','filename':filename,"ActionID":id}), 200
    except Exception as ex:
        logging.error(f"Error on downloading file {filename} ERROR :: {str(ex)}")
        return jsonify(f"Error on downloading file {filename} "),500


if __name__=='__main__':
    app.run(debug=True)
