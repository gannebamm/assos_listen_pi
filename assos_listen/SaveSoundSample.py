import pyaudio
import wave
import datetime
import signal
import ftplib
import sys
import os

# configuration for assos_listen
import config


# run the audio capture and send sound sample processes
# in parallel
from multiprocessing import Process

# CONFIG
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = config.samplingRate
RECORD_SECONDS = config.sampleLength

# HELPER FUNCTIONS

# write to ftp
def storeFile(filename):

    print("starting to upload file: " + filename)
    # connect to container
    ftp = ftplib.FTP(config.ftp_server_ip, config.username, config.password)

    # write file
    ftp.storbinary('STOR '+filename, open(filename, 'rb'))
    # close connection
    ftp.quit()
    print("finished uploading: " +filename)


# abort the sampling process
def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')

    # close stream and pyAudio
    stream.stop_stream()
    stream.close()
    p.terminate()

    sys.exit(0)

# MAIN FUNCTION
def recordAudio(p, stream):
    sampleNumber = 0
    while (sampleNumber < 6):
        print("*  recording")
        sampleNumber = sampleNumber +1

        frames = []
        startDateTimeStr = datetime.datetime.now().strftime("%Y_%m_%d_%I_%M_%S_%f")
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        fileName =  str(config.sensorID) + "_" + startDateTimeStr + ".wav"
        wf = wave.open(fileName, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print("file #"+str(sampleNumber)+" written")

        # since waiting for the upload to finish will take some time
        # and we do not want to have gaps in our sample
        # we start the upload process in parallel
        print("start uploading...")
        uploadProcess = Process(target=storeFile, args=(fileName,))
        uploadProcess.start()



# ENTRYPOINT FROM CONSOLE
if __name__ == '__main__':

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)


    # directory to write and read files from
    os.chdir(config.storagePath)

    # abort by pressing C
    signal.signal(signal.SIGINT, signal_handler)
    print('\n\n--------------------------\npress Ctrl+C to stop the recording')

    # start recording
    recordAudio(p, stream)