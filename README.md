# PyFtpServer
A simple FtpServer for RFC959 study purposes, wrote in python.
Tested on Python 2.7.9 with Linux as O.S.
The project is under development process is not secure neither failure prevent tested.


## Responding Commands (Not fully implemented yet)
- USER (anonymous only permitted for while)
- PASS (not checking but responding)
- PASV
- LIST
- CWD
- SYST
- TYPE
- PWD
- SIZE
- STOR
- RETR

### How to Use:
**$>python PyFtpServer.py**
The server will be listening on localhost at port 12020(not standard port, but in future should be).

You can log in only as user "anonymous" and anything as password.(multiuser not implemented yet)

The server will create a directory called "server" on the same directory where the file PyFtpServer.py resides.
In this "server" directory you can put files that you wish "RETR", or take the files that you have stored with "STOR" command previously.

