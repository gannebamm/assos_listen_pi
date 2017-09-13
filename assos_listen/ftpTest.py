import ftplib

filename = "output.wav"

# configuration for docker container
ftp_server_ip = "192.168.0.157"
username = "sensor"
password = "sensor"

# connect to container
ftp = ftplib.FTP(ftp_server_ip,username,password)

## works
#filename = "3MB.zip"
#ftp = ftplib.FTP('speedtest.tele2.net')
#ftp.login()

# write to ftp
def storeFile(filename):
    ftp.storbinary('STOR '+filename, open(filename, 'rb'))

# retrieve from ftp
def grabFile(filename):
    localfile = open(filename, 'wb')
    ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
    localfile.close()

# test
storeFile("output.wav")

grabFile("output_back.wav")

# close connection
ftp.quit()
