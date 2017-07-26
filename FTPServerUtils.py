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

"""TODO: Separar codigos das msgs"""

WELCOME_MSG = '220 Welcome!\r\n'
CMD_ERROR_MSG = '500 Syntax error, command unrecognized.\r\n'
GOODBYE_MSG = '221 Goodbye.\r\n'
USERNAME_OK_MSG = '331 User name okay, need password.\r\n'
USERNAME_ERROR_MSG = '530 Not logged in.Try anonymous or valid account\r\n'
PASSWORD_OK_MSG = '230 Password OK.User logged in.\r\n'
PASSWORD_ERROR_MSG = '530 Incorrect password.Not logged in.\r\n'
SYST_MSG = '215 UNIX Type: L8\r\n'
TYPESET_MSG = '200 Type set to %s.\r\n'
CURR_DIR_MSG = '257 "%s" is the current directory.\r\n'
NOT_A_FILE_MSG = '550 %s: not a regular file.\r\n'
DIR_CHANGED_MSG = '250 Directory changed.\r\n'
DIR_CHANGED_TO_ROOT_MSG = '250 Directory changed to root.\r\n'
PATH_NOT_FOUND_MSG = '550 Path not found.Directory not changed\r\n'
PATH_NOT_A_DIR_MSG = '550 Path is not a directory.Directory not changed\r\n'
NEED_PASV_OR_PORT_MSG = '425 Use PASV or PORT first.\r\n'
OPEN_DATA_CONN_MSG = '150 Opening data connection.\r\n'
TRANSFER_COMPLETE_MSG = '226 Transfer complete.\r\n'
DIR_LIST_MSG = '150 Here comes the directory listing.\r\n'
PASV_MODE_MSG = '227 Entering Passive Mode (%s,%u,%u).\r\n'

def fileModeStr(mode):
    fileModes = ["-","x","w","r"]
    resultStr = ""
    for i in range(8,-1,-1):
        check = ((mode >> i) & 1)
        resultStr += fileModes[check + check*(i%3)]
    return resultStr

def uploadFile(dataSocket,fileName, bufferSize):
        dataConnectionSocket, addr = dataSocket.accept()
            
        fileDescriptor = open(fileName, "rb")

        fileContent = fileDescriptor.read(bufferSize)
            
        while fileContent:
            dataConnectionSocket.send(fileContent)
            fileContent = fileDescriptor.read(bufferSize)
        
        fileDescriptor.close()
        dataConnectionSocket.close()

def downloadFile(dataSocket,fileName, bufferSize):
        
    dataConnectionSocket, addr = dataSocket.accept()
    fileDescriptor = open(fileName, "wb")
        
    while True:
        fileContent = dataConnectionSocket.recv(bufferSize)
            
        if(not fileContent): break
            
        fileDescriptor.write(fileContent)
            
    fileDescriptor.close()
    dataConnectionSocket.close()

    
def normalizePath(pathName,currDir, dirName):
    os.path.normpath(pathName)

    if(pathName == "."):
        return  currDir
                    
    if(pathName.startswith("/")):
        pathName = dirName + pathName
    else:
        pathName = currDir + "/"+ pathName
            
    pathName = os.path.realpath(pathName)

    rootPath = os.path.realpath(dirName)

    pathName = os.path.relpath(pathName,rootPath)

    if(pathName == ".."):
        pathName = ""
            
    while(pathName.startswith("../")):
        pathName = pathName.split("../",1)[1]
            
    if(pathName.startswith("..")):
        pathName = pathName.split("..",1)[1]
            
    pathName = dirName + "/" + pathName
            
    return os.path.normpath(pathName)
