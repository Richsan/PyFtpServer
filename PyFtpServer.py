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
#import sys
from os import listdir
from os.path import isfile, join
import os,time
import threading
import signal


class FTPServerUtilities:

    welcomeMsg = '220 Welcome!\r\n'
    cmdErrorMsg = '500 Syntax error, command unrecognized.\r\n'
    goodbyeMsg = '221 Goodbye.\r\n'
    userNameOkMsg = '331 User name okay, need password.\r\n'
    userNameErrorMsg = '530 Not logged in.Try anonymous or valid account\r\n'
    passwordOkMsg = '230 Password OK.User logged in.\r\n'
    passwordErrorMsg = '530 Incorrect password.Not logged in.\r\n'
    systMsg = '215 UNIX Type: L8\r\n'
    typeSetMsg = '200 Type set to %s.\r\n'
    currDirMsg = '257 "%s" is the current directory.\r\n'
    notFileMsg = '550 %s: not a regular file.\r\n'
    dirChangedMsg = '250 Directory changed.\r\n'
    dirChangedToRootMsg = '250 Directory changed to root.\r\n'
    pathNotFoundMsg = '550 Path not found.Directory not changed\r\n'
    pathNotDirMsg = '550 Path is not a directory.Directory not changed\r\n'
    needPasvOrPortMsg = '425 Use PASV or PORT first.\r\n'
    openDataConnMsg = '150 Opening data connection.\r\n'
    transferCompleteMsg = '226 Transfer complete.\r\n'
    dirListMsg = '150 Here comes the directory listing.\r\n'
    pasvModeMsg = '227 Entering Passive Mode (%s,%u,%u).\r\n'
    
    def fileModeStr(self,mode):
        fileModes = ["-","x","w","r"]
        resultStr = ""
        for i in range(8,-1,-1):
            check = ((mode >> i) & 1)
            resultStr += fileModes[check + check*(i%3)]
        return resultStr
    
#verificar em todos os metodos de cmd a quantidade de argumentos passados
class _ServerDTP(threading.Thread):
    __dirName = "server"
    __currDir = __dirName
    __dataPort = 1021
    __bufferSize = 1026
    __utils = FTPServerUtilities()
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
        self.conn.send(self.__utils.welcomeMsg)
        while True:
            self.cmd = self.conn.recv(bufferSize)
            self.command()
            if(self.__quitted):
                break

    def normalizePath(self,pathName):

        os.path.normpath(pathName)

        if(pathName == "."):
            return  self.__currDir
                    
        if(pathName.startswith("/")):
            pathName = self.__dirName + pathName
        else:
            pathName = self.__currDir + "/"+ pathName
            
        pathName = os.path.realpath(pathName)

        rootPath = os.path.realpath(self.__dirName)

        pathName = os.path.relpath(pathName,rootPath)

        if(pathName == ".."):
            pathName = ""
            
        while(pathName.startswith("../")):
            pathName = pathName.split("../",1)[1]
            
        if(pathName.startswith("..")):
            pathName = pathName.split("..",1)[1]
            
        pathName = self.__dirName + "/" + pathName
            
        return os.path.normpath(pathName)


    def command(self):
        cmd = self.cmd
        print "Received: "+cmd

        def default_act():
            self.conn.send(self.__utils.cmdErrorMsg)
            
        action = getattr(self,cmd.split(" ")[0].strip().upper(),default_act)
        action()
         
            

    def QUIT(self):
        self.__quitted = True
        self.conn.send(self.__utils.goodbyeMsg)
        self.conn.close()
        
    def USER(self):
        [cmd,userName] = self.cmd.strip().split()
        if(userName == 'anonymous'):
            self.conn.send(self.__utils.userNameOkMsg)
        else:
            self.conn.send(self.__utils.userNameErrorMsg)

            
    def PASS(self):
        self.conn.send(self.__utils.passwordOkMsg)
        #self.conn.send(self.__utils.passwordErrorMsg)


    def SYST(self):
        self.conn.send(self.__utils.systMsg)

        
    def TYPE(self):
        [cmd,self.__type] = self.cmd.strip().split()
        self.conn.send(self.__utils.typeSetMsg % self.__type)


    def PWD(self):
        currPath = self.__currDir.split(self.__dirName,1)[1] + "/"
        self.conn.send(self.__utils.currDirMsg % currPath)


    def SIZE(self):
        [cmd,nameFile] = self.cmd.strip().split()

        nameFile = self.normalizePath(nameFile)
        
        if(not os.path.isdir(nameFile)):
            sizeFile = os.path.getsize(nameFile)
            self.conn.send('213 '+str(sizeFile)+'\r\n')
        else:
            self.conn.send(self.__utils.notFileMsg % nameFile)

    #verificar se eh retrocesso, caminho absoluto ou relativo
    def CWD(self):
        [cmd, pathName] = self.cmd.strip().split()

        pathName = self.normalizePath(pathName)

        
        if(not os.path.exists(pathName)):
            self.conn.send(self.__utils.pathNotFoundMsg)
            return
            
        elif(not os.path.isdir(pathName)):
            self.conn.send(self.__utils.pathNotDirMsg)
            return

        else:
            self.__currDir = pathName
            self.conn.send(self.__utils.dirChangedMsg)
            return

    def STOR(self):
        if(not self.__pasv):
            self.conn.send(self.__utils.needPasvOrPortMsg)
            return
        
        [cmd,nameFile] = self.cmd.strip().split()
        nameFile = self.normalizePath(nameFile)

        bufferSize = self.__bufferSize

        fileDescriptor = open(nameFile, "wb")
        
        self.conn.send(self.__utils.openDataConnMsg)
        
        dataConnectionSocket, addr = self.__dataSocket.accept()
        
        while True:
            fileContent = dataConnectionSocket.recv(bufferSize)
            
            if(not fileContent): break
            
            fileDescriptor.write(fileContent)
        
        fileDescriptor.close()
        dataConnectionSocket.close()
        self.conn.send(self.__utils.transferCompleteMsg)
        self.__pasv = False

    #verificar se existe arquivo e se eh arquivo
    #talvez tenha que fazer transferencia em uma thread diferente
    #p/ poder haver abort
    def RETR(self):
        if(not self.__pasv):
            self.conn.send(self.__utils.needPasvOrPortMsg)
            return
    
        [cmd,nameFile] = self.cmd.strip().split()
        nameFile = self.normalizePath(nameFile)
        bufferSize = self.__bufferSize

        self.conn.send(self.__utils.openDataConnMsg)

        dataConnectionSocket, addr = self.__dataSocket.accept()
            
        fileDescriptor = open(nameFile, "rb")

        fileContent = fileDescriptor.read(bufferSize)
            
        while fileContent:
            dataConnectionSocket.send(fileContent)
            fileContent = fileDescriptor.read(bufferSize)
        
        fileDescriptor.close()
        dataConnectionSocket.close()
        self.conn.send(self.__utils.transferCompleteMsg)
        self.__pasv = False 

        
    def LIST(self):
        if(not self.__pasv):
            self.conn.send(self.__utils.needPasvOrPortMsg)
            return
        
        self.conn.send(self.__utils.dirListMsg)
        dataConnectionSocket, addr = self.__dataSocket.accept()

        for f in listdir(self.__currDir):
            st = os.stat(self.__currDir+"/"+f)
            mode = self.__utils.fileModeStr(st.st_mode)
            d = "d"

            if(not os.path.isdir(self.__currDir+"/"+f)):
                d = "-"
                
            sizeFile = str(st.st_size)
            ftime = time.strftime(' %b %d %H:%M ', time.gmtime(st.st_mtime))
            textList = d+mode+' 1 user group '+sizeFile+ftime+f+'\r\n'
            dataConnectionSocket.send(textList)
        
        dataConnectionSocket.close()
        self.conn.send(self.__utils.transferCompleteMsg)
        self.__pasv = False     
        
    def PASV(self):
        if(self.__pasv):
            self.__dataSocket.close()
            self.__pasv = False

        self.__dataSocket = socket(AF_INET, SOCK_STREAM)
        self.__dataSocket.bind((self.__hostname,0))
        self.__dataSocket.listen(1)
        ip, port = self.__dataSocket.getsockname()
        self.conn.send(self.__utils.pasvModeMsg %
                (','.join(ip.split('.')), port >>8 & 0xFF, port & 0xFF))
        self.__pasv = True

        
class ServerPI:
    
    __controlPort = 12020    
    __controlSocket = socket(AF_INET, SOCK_STREAM)
    __FTPDir = "server"
    
    def __init__(self, hostname = ''):
        print 'Server Started'

        self.__controlSocket.bind((hostname,self.__controlPort))
        self.__controlSocket.listen(5)
        
        while True:
            DTP = _ServerDTP(self.__controlSocket.accept(), hostname)
            DTP.start()
      
            
    def __del__(self):
        self.__controlSocket.close()

def FTPServer(hostname = ''):
    return ServerPI(hostname)

#pegar argv talvez e tratar excessao de sigkill
if __name__=='__main__':
    ftpServer = FTPServer()
