from socket import *
import requests,configparser,logging,threading
conf=configparser.ConfigParser()
conf.read("configs.ini")
class TCPConnection:
    def __init__(self,destaddr:str=conf.get("AppConfig","ultratcp"),destport:int=int(conf.get("AppConfig","ultratcp_port"))) -> None:
        self.sock=socket(AF_INET,SOCK_STREAM)
        self.sock.connect((destaddr,destport))
        self.chunkiter=0
        self.connID=0
        self.byteCounter=0
    def send(self,data:bytes):
        self.sock.sendall(data)
        if self.chunkiter==0:
            self.connID=int(self.sock.recv(256).decode())
        self.chunkiter+=1
        self.byteCounter+=len(data)
        
    def get_id(self):
        print(self.connID)
        return self.connID
    def send_in_thread(self,data:bytes):
        tr=threading.Thread(target=self.send,args=(data,))
        tr.run()
        
    def save_file(self,filename:str):
        resp=requests.post(conf.get("AppConfig","ultratcpurl")+f"/save/file/{filename}/{self.connID}")
        if "Chunks written" in resp.text:
            print("successfully written")
        else:
            logging.error(f"Error on writing by UltraTCP Response [code {resp.status_code}] is::{resp.text}")
            print(f"Error on writing by UltraTCP Response [code {resp.status_code}] is::{resp.text}")
    def disconnect(self):
        self.sock.close()