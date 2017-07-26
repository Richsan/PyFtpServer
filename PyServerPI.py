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

from PyServerDTP import ServerDTP, log
from socket import *

class ServerPI:
    
    __controlPort = 12020    
    __controlSocket = socket(AF_INET, SOCK_STREAM)
    __FTPDir = "server"
    
    def __init__(self, hostname = ''):
        log.info('Server Started')

        self.__controlSocket.bind((hostname,self.__controlPort))
        self.__controlSocket.listen(5)
        
        while True:
            DTP = ServerDTP(self.__controlSocket.accept(), hostname)
            DTP.start()
      
            
    def __del__(self):
        self.__controlSocket.close()
