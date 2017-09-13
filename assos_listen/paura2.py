import sys, os, time, numpy, glob, scipy, subprocess, wave, cPickle, threading, shutil, cv2
import argparse
import scipy.io.wavfile as wavfile
from scipy.fftpack import rfft
from pyAudioAnalysis import audioFeatureExtraction as aF
from pyAudioAnalysis import audioTrainTest as aT
from pyAudioAnalysis import audioSegmentation as aS
from scipy.fftpack import fft
import scipy.signal
import itertools
import operator
import datetime
import signal
import pyaudio  # PORT-AUDIO-BASED
import struct
import math

import ftplib
import config

Fs = config.Fs

FORMAT = pyaudio.paInt16
allData = []

# write to ftp
def storeFile(filename):
    # connect to container
    ftp = ftplib.FTP(config.ftp_server_ip, config.username, config.password)
    # write file
    ftp.storbinary('STOR '+filename, open(filename, 'rb'))
    # close connection
    ftp.quit()


def signal_handler(signal, frame):
    wavfile.write(str(config.sensorID) + "_output.wav", Fs, numpy.int16(allData))  # write final buffer to wav file
    print('You pressed Ctrl+C!')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

'''
Utitlity functions:
'''


def loadMEANS(modelName):
    # load pyAudioAnalysis classifier file (MEAN and STD values).
    # used for feature normalization
    try:
        fo = open(modelName, "rb")
    except IOError:
        print "Load Model: Didn't find file"
        return
    try:
        MEAN = cPickle.load(fo)
        STD = cPickle.load(fo)
    except:
        fo.close()
    fo.close()
    return (MEAN, STD)


def most_common(L):
    # get an iterable of (item, iterable) pairs
    SL = sorted((x, i) for i, x in enumerate(L))
    # print 'SL:', SL
    groups = itertools.groupby(SL, key=operator.itemgetter(0))

    # auxiliary function to get "quality" for an item
    def _auxfun(g):
        item, iterable = g
        count = 0
        min_index = len(L)
        for _, where in iterable:
            count += 1
            min_index = min(min_index, where)
        # print 'item %r, count %r, minind %r' % (item, count, min_index)
        return count, -min_index

    # pick the highest-count/earliest item
    return max(groups, key=_auxfun)[0]


'''
Basic functionality:
'''


def recordAudioSegments(BLOCKSIZE, Fs=16000):
    midTermBufferSize = int(Fs * BLOCKSIZE)

    print "Press Ctr+C to stop recording"

    startDateTimeStr = datetime.datetime.now().strftime("%Y_%m_%d_%I:%M%p")

    MEAN, STD = loadMEANS("svmMovies8classesMEANS")  # load MEAN feature values

    pa = pyaudio.PyAudio()

    stream = pa.open(format=FORMAT,
                     channels=1,
                     rate=Fs,
                     input=True,
                     frames_per_buffer=midTermBufferSize)

    midTermBuffer = []
    curWindow = []
    count = 0
    global allData
    allData = []
    energy100_buffer_zero = []
    curActiveWindow = numpy.array([])
    timeStart = time.time()

    while 1:
        try:
            block = stream.read(midTermBufferSize)
            countB = len(block) / 2
            format = "%dh" % (countB)
            shorts = struct.unpack(format, block)
            curWindow = list(shorts)
            midTermBuffer = midTermBuffer + curWindow;  # copy to midTermBuffer
            del (curWindow)
            # print len(midTermBuffer), midTermBufferSize
            # if len(midTermBuffer) == midTermBufferSize:                                     # if midTermBuffer is full:
            if 1:
                elapsedTime = (time.time() - timeStart)  # time since recording started
                dataTime = (count + 1) * BLOCKSIZE  # data-driven time

                # TODO
                # mtF, _ = aF.mtFeatureExtraction(midTermBuffer, Fs, BLOCKSIZE * Fs, BLOCKSIZE * Fs, 0.050 * Fs, 0.050 * Fs)
                # curFV = (mtF - MEAN) / STD
                # TODO
                allData += midTermBuffer
                midTermBuffer = numpy.double(midTermBuffer)  # convert current buffer to numpy array

                # Activity Detection:
                energy100 = (100 * numpy.sum(midTermBuffer * midTermBuffer)
                             / (midTermBuffer.shape[0] * 32000 * 32000))
                if count < 10:  # TODO make this param
                    energy100_buffer_zero.append(energy100)
                    mean_energy100_zero = numpy.mean(numpy.array(energy100_buffer_zero))
                else:
                    mean_energy100_zero = numpy.mean(numpy.array(energy100_buffer_zero))
                    if (energy100 < 1.2 * mean_energy100_zero):
                        if curActiveWindow.shape[0] > 0:  # if a sound has been detected in the previous segment:
                            activeT2 = elapsedTime - BLOCKSIZE  # set time of current active window
                            if activeT2 - activeT1 > config.minActivityDuration:
                                wavFileName = str(config.sensorID) + "_" + "_activity_{0:.2f}_{1:.2f}.wav".format(activeT1,
                                                                                                        activeT2)
                                print("loud enough ... write file")
                                wavfile.write(wavFileName, Fs,
                                                  numpy.int16(curActiveWindow))  # write current active window to file

                                # sent to assos_storage container
                                print("sending file to assos_storage container")
                                #storeFile(wavFileName)

                            curActiveWindow = numpy.array([])  # delete current active window
                    else:
                        if curActiveWindow.shape[0] == 0:  # this is a new active window!
                            activeT1 = elapsedTime - BLOCKSIZE  # set timestamp start of new active window
                        curActiveWindow = numpy.concatenate((curActiveWindow, midTermBuffer))

                midTermBuffer = []
                count += 1

        except IOError, e:
            print("(Error recording: %s" % (e))


if __name__ == "__main__":
    global Fs
    Fs = config.Fs
    recordAudioSegments(config.Bs, Fs)
