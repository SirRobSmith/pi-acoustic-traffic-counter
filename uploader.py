""" This tool runs continously on a Raspberry Pi3 computer
and performs the basic function of identifying when an accoustic
beam has been broken, logs it as an event and ships those logs to
a remote server for analysis  """

from ftplib import FTP
import os
from datetime import datetime

# Other runtime-y stuff
NOW                     = datetime.now()
readable_date           = NOW.strftime("%m/%d/%Y, %H:%M:%S")

# FTP variables
FTP_SERVER              = os.environ["FTP_SERVER"]
FTP_USER                = os.environ["FTP_USER"]
FTP_PASS                = os.environ["FTP_PASS"]
FTP_RELATIVE_DIR        = os.environ["FTP_RELATIVE_DIR"]

# Settings local to the Pi
CACHE_DIR   = "/Users/rob/pi-acoustic-traffic-counter/cache"
LOG_LOCATION = "log.log"


def log_progress(log_message):
    """
    Log a message to a file
    :param log_message: the message to log
    """
    with open(f'{LOG_LOCATION}', "a", encoding="utf-8") as f:
        f.write(str(readable_date)+" | "+log_message+"\r\n")
        f.close()

def ship_logs():
    """ 
    The computer will have infrequent access to the internet, and as such will 
    attempt to ship stored data when network connectivity is in place """

    # Connect to the FTP server using the pre-defined credentials
    ftp = FTP(host=FTP_SERVER, user=FTP_USER, passwd=FTP_PASS)

    # Jump to the correct directory
    ftp.cwd(FTP_RELATIVE_DIR)

    # Loop through each file waiting to be processed
    for file in os.listdir(CACHE_DIR+"/queue"):

        # Establish the name of the file
        filename = os.fsdecode(file)

        # Reference the file
        with open(f'{CACHE_DIR}/queue/{filename}', "rb") as filedata:

            # Try and upload the file to the FTP server
            try:
                ftp.storbinary(f'STOR {filename}', filedata)
            except: 
                # The file failed to upload.
                log_progress(f'File {filename} failed to upload')
            else:
                # The file uploaded without error, move the file to the completed director
                os.replace(CACHE_DIR+"/queue/"+filename, CACHE_DIR+"/complete/"+filename)
                log_progress(f'File {filename} successfully uploaded')

if __name__ == "__main__":

    ship_logs()