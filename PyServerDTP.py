""""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from socket import *
from os import listdir
from os.path import isfile, join
import os,time
import threading
import signal
import FTPServerUtils as utils
import PyFTPServerLogging as log


class ServerDTP(threading.Thread):
    __dirName = "server"
    __currDir = __dirName
    __dataPort = 1021
    __bufferSize = 1026
    __quitted = False
    __pasv = False
    
    def __init__(self,(conn,addr),hostname):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.__hostname = hostname

        if not os.path.exists(self.__dirName):
            os.makedirs(self.__dirName)
        
    def run(self):
        bufferSize = self.__bufferSize
        self.conn.send(utils.WELCOME_MSG)
        while True:
            self.cmd = self.conn.recv(bufferSize)
            self.command()
            if(self.__quitted):
                break


    def command(self):
        cmd = self.cmd
        print "Received: "+cmd

        def default_act():
            self.conn.send(utils.CMD_ERROR_MSG)
            
        action = getattr(self,cmd.split(" ")[0].strip().upper(),default_act)
        action()
         
            

    def QUIT(self):
        self.__quitted = True
        self.conn.send(utils.GOODBYE_MSG)
        self.conn.close()
        
    def USER(self):
        [cmd,userName] = self.cmd.strip().split()
        if(userName == 'anonymous'):
            self.conn.send(utils.USERNAME_OK_MSG)
        else:
            self.conn.send(utils.USERNAME_ERROR_MSG )

            
    def PASS(self):
        self.conn.send(utils.PASSWORD_OK_MSG)
        #self.conn.send(utils.PASSWORD_ERROR_MSG)


    def SYST(self):
        self.conn.send(utils.SYST_MSG)

        
    def TYPE(self):
        [cmd,self.__type] = self.cmd.strip().split()
        self.conn.send(utils.TYPESET_MSG % self.__type)


    def PWD(self):
        currPath = self.__currDir.split(self.__dirName,1)[1] + "/"
        self.conn.send(utils.CURR_DIR_MSG % currPath)


    def SIZE(self):
        [cmd,nameFile] = self.cmd.strip().split()

        nameFile = self.normalizePath(nameFilee,self.__currDir,self.__dirName)
        
        if(not os.path.isdir(nameFile)):
            sizeFile = os.path.getsize(nameFile)
            self.conn.send('213 '+str(sizeFile)+'\r\n')
        else:
            self.conn.send(utils.NOT_A_FILE_MSG % nameFile)

   
    def CWD(self):
        [cmd, pathName] = self.cmd.strip().split()

        pathName = self.normalizePath(pathNamee,self.__currDir,self.__dirName)

        
        if(not os.path.exists(pathName)):
            self.conn.send(utils.PATH_NOT_FOUND_MSG)
            return
            
        elif(not os.path.isdir(pathName)):
            self.conn.send(utils.PATH_NOT_A_DIR_MSG)
            return

        else:
            self.__currDir = pathName
            self.conn.send(utils.DIR_CHANGED_MSG)
            return

    def STOR(self):
        if(not self.__pasv):
            self.conn.send(utils.NEED_PASV_OR_PORT_MSG)
            return
        
        [cmd,nameFile] = self.cmd.strip().split()
        filename = self.normalizePath(fileNamee,self.__currDir,self.__dirName)

        bufferSize = self.__bufferSize
        
        self.conn.send(utils.OPEN_DATA_CONN_MSG)

        utils.downloadFile(self.__dataSocket,fileName,bufferSize)
        
        self.conn.send(utils.TRANSFER_COMPLETE_MSG)
        self.__pasv = False

        
    def RETR(self):
        if(not self.__pasv):
            self.conn.send(utils.NEED_PASV_OR_PORT_MSG)
            return
    
        [cmd,fileName] = self.cmd.strip().split()
        fileName = utils.normalizePath(fileName,self.__currDir,self.__dirName)
        bufferSize = self.__bufferSize

        self.conn.send(utils.OPEN_DATA_CONN_MSG)

        utils.uploadFile(self.__dataSocket,fileName,bufferSize)
        
        self.conn.send(utils.TRANSFER_COMPLETE_MSG)
        self.__pasv = False 

        
    def LIST(self):
        if(not self.__pasv):
            self.conn.send(utils.NEED_PASV_OR_PORT_MSG)
            return
        
        self.conn.send(utils.DIR_LIST_MSG)
        dataConnectionSocket, addr = self.__dataSocket.accept()

        for f in listdir(self.__currDir):
            st = os.stat(self.__currDir+"/"+f)
            mode = utils.fileModeStr(st.st_mode)
            d = "d"

            if(not os.path.isdir(self.__currDir+"/"+f)):
                d = "-"
                
            sizeFile = str(st.st_size)
            ftime = time.strftime(' %b %d %H:%M ', time.gmtime(st.st_mtime))
            textList = d+mode+' 1 user group '+sizeFile+ftime+f+'\r\n'
            dataConnectionSocket.send(textList)
        
        dataConnectionSocket.close()
        self.conn.send(utils.TRANSFER_COMPLETE_MSG)
        self.__pasv = False     
        
    def PASV(self):
        if(self.__pasv):
            self.__dataSocket.close()
            self.__pasv = False

        self.__dataSocket = socket(AF_INET, SOCK_STREAM)
        self.__dataSocket.bind((self.__hostname,0))
        self.__dataSocket.listen(1)
        ip, port = self.__dataSocket.getsockname()
        self.conn.send(utils.PASV_MODE_MSG %
                (','.join(ip.split('.')), port >>8 & 0xFF, port & 0xFF))
        self.__pasv = True
