from flask import Flask,jsonify,Response
from flask_cors import CORS
from flask import Flask, request, jsonify
import os,hashlib,secrets,time
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
CORS(app)
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
    download_thread =threading.Thread(target=download_file_with_progress_limited, args=(url,destination_path,id,int(chunksize)))
    download_thread.start()
    #Files_inprogress[id]["tr"]=download_thread

    return jsonify({'message':'Download started','filename':filename,"ActionID":id}), 200


def generate(ActionID):
    progress_percent=0
    
    while progress_percent<=100:
        time.sleep(0.4)
        if progress_percent==100:
            yield  "event: close\ndata: \n\n" 
        destination_path =f"downloads/{Files_inprogress[ActionID]['filename']}"
        if os .path.exists(destination_path):
            expected_file_size=Files_inprogress[ActionID]["dl"]
            downloaded_file_size=round(float(os.path.getsize(destination_path)/(1024*1024)),2) #convert bytes to MB
            progress_percent =(float(downloaded_file_size) / float(expected_file_size))*100
        yield f"data: {{'progress': {progress_percent}}}\n\n"


@app.route('/progress1/<ActionID>')
@app.route("/update_progress/<ActionID>")
def update_progress(ActionID):
    return Response(generate(ActionID), content_type="text/event-stream")
@app.route('/progress/<ActionID>')
def progress(ActionID):
    # Assuming the progress is calculated based on the downloaded file size compared to the expected file size
    try:
        destination_path =f"downloads/{Files_inprogress[ActionID]['filename']}"
    except KeyError:
        logging.error("*Error on selecting file in progress maybe it is finished & removed. Error: "+str(ex))
        return jsonify("*Error on selecting file in progress maybe it is finished & removed."),500
    except Exception as ex:
        import logging
        logging.error("Error on selecting file in progress maybe it is finished & removed. Error: "+str(ex))
        return jsonify("Error on selecting file in progress maybe it is finished & removed."),500
    if os.path.exists(destination_path):
        expected_file_size=Files_inprogress[ActionID]["dl"]
        if expected_file_size:
            if int(expected_file_size)<1:
                return jsonify({'progress': 100}),200
            downloaded_file_size=round(float(os.path.getsize(destination_path)/(1024*1024)),2) #convert bytes to MB
            
            progress_percent =(float(downloaded_file_size) / float(expected_file_size))*100
            return jsonify({'progress': int(progress_percent)}), 200

    return jsonify({'error':'File not found or progress unavailable'}), 404

@app.route("/finish/<ActionID>",methods=["POST"])
def finish_action(ActionID):
    #Files_inprogress[ActionID]["dl"]=0#we make it zero because the File might be deleted
    print("finished registered",ActionID)
    return jsonify("finished registered "+str(ActionID))
@app.route('/selectall')
def selectall():
    return jsonify(Files_inprogress)
#@app.route('/delete/<actionid>')
#def deleting(actionid):
#    del Files_inprogress[actionid]

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
        download_thread =threading.Thread(target=download_file_with_progress_limited, args=(url,destination_path,id,int(chunksize)))
        download_thread.start()
        #Files_inprogress[id]["tr"]=download_thread

        return jsonify({'message':'Download started','filename':filename,"ActionID":id}), 200
    except Exception as ex:
        logging.error(f"Error on downloading file {filename} ERROR :: {str(ex)}")
        return jsonify(f"Error on downloading file {filename} "),500


if __name__=='__main__':
    app.run(host="0.0.0.0",port=1001,debug=True)
