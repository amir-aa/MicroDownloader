import requests,logging
from tqdm import tqdm  
import datetime,time
import configparser
from client import TCPConnection
conf=configparser.ConfigParser()
conf.read("configs.ini")
def download_file_with_progress(url, destination,action_id,chunksize=8192):
    try:
        response = requests.head(url)
        response.raise_for_status()

        content_length = response.headers.get('Content-Length')
        if content_length is None:
            print("Cannot determine file size.")
            raise Exception("Cannot determine file size.")
        else:
            file_size = int(content_length)
            print(f"File size: {file_size / (1024 * 1024):.2f} MB")

        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            tcp_connection=TCPConnection()
            with open(destination, 'wb') as file, tqdm(
                desc="Downloading",
                total=file_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=chunksize):
                    tcp_connection.send(chunk)#send to ultraTCP
                    tcp_connection.disconnect()
                    del tcp_connection
                    file.write(chunk)
                    progress_bar.update(len(chunk))

        print(f"File downloaded successfully to {destination}")
        logging.info(f"File downloaded successfully to {destination}")
        requests.post(f"{conf.get('AppConfig','bind_url')}/finish/{action_id}")
    except requests.exceptions.RequestException as ex:
        print(f"Error downloading the file: {ex}")

def download_file_with_progress_limited(url, destination,action_id,chunksize=8192):
    try:
        response = requests.head(url)
        response.raise_for_status()

        content_length=response.headers.get('Content-Length')
        if content_length is None:
            print("Cannot determine file size.")
            raise Exception("Cannot determine file size.")
        else:
            file_size = int(content_length)
            print(f"File size: {file_size / (1024 * 1024):.2f} MB")

        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            tcp_connection=TCPConnection()
            LIMIT=float(conf.get("AppConfig","MBpslimit")) #MBps
            Limit_cycle=((LIMIT*1024)/(chunksize//1024))*60 # Howmany chunks should be downloaded in a minute
            starttime=datetime.datetime.now()
            _iterator=0
            with open(destination, 'wb') as file,tqdm(
                desc="Downloading",
                total=file_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=chunksize):
                    tcp_connection.send(chunk)#send to ultraTCP
                    tcp_connection.disconnect()
                    del tcp_connection
                    file.write(chunk)
                    progress_bar.update(len(chunk))
                    _iterator+=1
                    if _iterator>Limit_cycle:
                        executed_time=datetime.datetime.now()-starttime
                        time.sleep(60-executed_time.seconds)
                        print(f"Thread {destination} wainting to regulate speed")
                        _iterator=0
                        starttime=datetime.datetime.now()

        print(f"File downloaded successfully to {destination}")
        logging.info(f"File downloaded successfully to {destination}")
        requests.post(f"{conf.get('AppConfig','bind_url')}/finish/{action_id}")
    except requests.exceptions.RequestException as ex:
        print(f"Error downloading the file: {ex}")
