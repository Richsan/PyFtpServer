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


import logging

INFO_LOG_FILENAME = 'PyFtpserverInfo.log'
ERROR_LOG_FILENAME = 'PyFtpserverErrors.log'


logging.basicConfig(filename=INFO_LOG_FILENAME,format='%(levelname)s:%(message)s',level=logging.INFO)
logging.basicConfig(filename=INFO_LOG_FILENAME,format='%(levelname)s:%(message)s',level=logging.WARNING)
logging.basicConfig(filename=INFO_LOG_FILENAME,format='%(levelname)s:%(message)s',level=logging.DEBUG)
logging.basicConfig(filename=ERROR_LOG_FILENAME,format='%(levelname)s:%(message)s',level=logging.ERROR)
logging.basicConfig(filename=ERROR_LOG_FILENAME,format='%(levelname)s:%(message)s',level=logging.CRITICAL)
