### configuration file for assos_listen

# config for this sensor
sensorID = "al_01"

# sampling rate
samplingRate = 16000 # 44100 is to much for raspberry pi 3
# choices=[4000, 8000, 16000, 32000, 44100] :: default 16000

# sample length in seconds
sampleLength = 10

# configuration for assos_store container
ftp_server_ip = "192.168.0.157"
username = "sensor"
password = "sensor"

# storage on assos_listen device
storagePath = "/home/pi/assos_listen_pi/storage/"