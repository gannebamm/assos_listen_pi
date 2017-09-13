### configuration file for assos_listen

# config for this sensor
sensorID = "al_01"

# record activity duration and energy
minActivityDuration = 0.5 #default 1.0
minEnergyToRecord = 2 #default 10

# sampling rate
Fs = 16000
# choices=[4000, 8000, 16000, 32000, 44100] :: default 16000
# blocksizte
Bs = 0.40
# choices=[0.1, 0.2, 0.3, 0.4, 0.5] :: default 0.2

# configuration for assos_store container
ftp_server_ip = "192.168.0.157"
username = "sensor"
password = "sensor"

# storage on assos_listen device
storagePath = "/home/pi/assos_listen_pi/storage/"