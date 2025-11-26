#!/usr/bin/python3

import btfpy
import threading
import time
import socket
import os

socket_path = '/tmp/my_socket'

class videoFaceCmd(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        try:
            os.unlink(socket_path)
        except OSError:
            if os.path.exists(socket_path):
                raise
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(socket_path)
        self.server.listen(1)
        self.runFlag = True
        cmd = 'chmod a+rw ' + socket_path
        os.system(cmd)
        
    def run(self):
        connection, client_address = self.server.accept()     
        while self.runFlag:
            data = connection.recv(1024)
            if not data:
                break
            key = int(data.decode())
            send_key(key)

        connection.close()
        os.unlink(socket_path)
            
reportmap = [0x05,0x01,0x09,0x06,0xA1,0x01,0x85,0x01,0x05,0x07,0x19,0xE0,0x29,0xE7,0x15,0x00,\
             0x25,0x01,0x75,0x01,0x95,0x08,0x81,0x02,0x95,0x01,0x75,0x08,0x81,0x01,0x95,0x06,\
             0x75,0x08,0x15,0x00,0x25,0x65,0x05,0x07,0x19,0x00,0x29,0x65,0x81,0x00,0xC0]

report = [0,0,0,0,0,0,0,0]

name = "Raspberry-HID"
appear = [0xC1,0x03]  # 03C1 = keyboard icon appears on connecting device 
pnpinfo = [0x02,0x6B,0x1D,0x46,0x02,0x37,0x05]
protocolmode = [0x01]
hidinfo = [0x01,0x11,0x00,0x02]
battery = [100] 
reportindex = -1
node = 0

def lecallback(clientnode,op,cticn):
    
  if(op == btfpy.LE_CONNECT):
    print("Connected OK. ESC stops server")

  if(op == btfpy.LE_KEYPRESS):
    send_key(cticn)      
 
  if(op == btfpy.LE_DISCONNECT):
    return(btfpy.SERVER_EXIT)
  return(btfpy.SERVER_CONTINUE)
 
def send_key(key):
  global reportindex
  global node
  
  print(key)
  # convert btferret code (key) to HID code  
  hidcode = btfpy.Hid_key_code(key)
  if(hidcode == 0):
    return

  buf = [0,0,0,0,0,0,0,0] 
        
  # send key press to Report1
  buf[0] = (hidcode >> 8) & 0xFF  # modifier
  buf[2] = hidcode & 0xFF         # key code
  btfpy.Write_ctic(node,reportindex,buf,0)
  # send no key pressed - all zero
  buf[0] = 0
  buf[2] = 0
  btfpy.Write_ctic(node,reportindex,buf,0) 
  return

############ START ###########
   
if(btfpy.Init_blue("keyboard.txt") == 0):
  exit(0)

if(btfpy.Localnode() != 1):
  print("ERROR - Edit keyboard.txt to set ADDRESS = " + btfpy.Device_address(btfpy.Localnode()))
  exit(0)
      
node = btfpy.Localnode()    

# look up Report1 index
uuid = [0x2A,0x4D]
reportindex = btfpy.Find_ctic_index(node,btfpy.UUID_2,uuid)
if(reportindex < 0):
  print("Failed to find Report characteristic")
  exit(0)

  # Write data to local characteristics  node=local node
uuid = [0x2A,0x00]
btfpy.Write_ctic(node,btfpy.Find_ctic_index(node,btfpy.UUID_2,uuid),name,0) 

uuid = [0x2A,0x01]
btfpy.Write_ctic(node,btfpy.Find_ctic_index(node,btfpy.UUID_2,uuid),appear,0) 

uuid = [0x2A,0x4E]
btfpy.Write_ctic(node,btfpy.Find_ctic_index(node,btfpy.UUID_2,uuid),protocolmode,0)

uuid = [0x2A,0x4A]
btfpy.Write_ctic(node,btfpy.Find_ctic_index(node,btfpy.UUID_2,uuid),hidinfo,0)

uuid = [0x2A,0x4B]
btfpy.Write_ctic(node,btfpy.Find_ctic_index(node,btfpy.UUID_2,uuid),reportmap,0)

uuid = [0x2A,0x4D]
btfpy.Write_ctic(node,btfpy.Find_ctic_index(node,btfpy.UUID_2,uuid),report,0)

uuid = [0x2A,0x50]
btfpy.Write_ctic(node,btfpy.Find_ctic_index(node,btfpy.UUID_2,uuid),pnpinfo,0)
   
randadd = [0xD3,0x56,0xD6,0x74,0x33,0x04]
btfpy.Set_le_random_address(randadd)
     
btfpy.Keys_to_callback(btfpy.KEY_ON,0)

btfpy.Set_le_wait(20000)  # 20 sec to complete
                                         
btfpy.Le_pair(btfpy.Localnode(),btfpy.JUST_WORKS,0) 

face_th = videoFaceCmd()
face_th.start()

btfpy.Le_server(lecallback, 1)

face_th.runFlag=False
face_th.join()

btfpy.Close_all()
