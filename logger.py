## Libraries ##
import smtplib
from sense_hat import SenseHat
from datetime import datetime

## Logging Settings ##

FILENAME = ""
WRITE_FREQUENCY = 50
TEMP_H_LOW = 10
TEMP_H_HIGH = 40
TEMP_P_LOW = 10
TEMP_P_HIGH = 40
HUMIDITY_LOW = 20
HUMIDITY_HIGH = 60
ALARM_FREQUENCY = 50000
DISPLAY_FREQUENCY = 1000

## Functions ##

def sendemail(from_addr, to_addr_list, cc_addr_list,
	subject, message,
	login, password,
	smtpserver='smtp.gmail.com:587'):
	header  = 'From: %s\n' % from_addr
	header += 'To: %s\n' % ','.join(to_addr_list)
	header += 'Cc: %s\n' % ','.join(cc_addr_list)
	header += 'Subject: %s\n\n' % subject
	message = header + message
 
	server = smtplib.SMTP(smtpserver)
	server.starttls()
	server.login(login,password)
	problems = server.sendmail(from_addr, to_addr_list, message)
	server.quit()
	return problems

def log_data():
	output_string = ",".join(str(value) for value in sense_data)
	batch_data.append(output_string)

def file_setup(filename):
	header  =["temp_h","temp_p","humidity","pressure",
	"pitch","roll","yaw",
	"mag_x","mag_y","mag_z",
	"accel_x","accel_y","accel_z",
	"gyro_x","gyro_y","gyro_z",
	"timestamp"]

	with open(filename,"w") as f:
		f.write(",".join(str(value) for value in header)+ "\n")

def get_sense_data():
	sense_data=[]

	sense_data.append(sense.get_temperature_from_humidity())
	sense_data.append(sense.get_temperature_from_pressure())
	sense_data.append(sense.get_humidity())
	sense_data.append(sense.get_pressure())

	o = sense.get_orientation()
	yaw = o["yaw"]
	pitch = o["pitch"]
	roll = o["roll"]
	sense_data.extend([pitch,roll,yaw])

	mag = sense.get_compass_raw()
	mag_x = mag["x"]
	mag_y = mag["y"]
	mag_z = mag["z"]
	sense_data.extend([mag_x,mag_y,mag_z])

	acc = sense.get_accelerometer_raw()
	x = acc["x"]
	y = acc["y"]
	z = acc["z"]
	sense_data.extend([x,y,z])

	gyro = sense.get_gyroscope_raw()
	gyro_x = gyro["x"]
	gyro_y = gyro["y"]
	gyro_z = gyro["z"]
	sense_data.extend([gyro_x,gyro_y,gyro_z])

	sense_data.append(datetime.now())

	return sense_data

## Main Program ##

sense = SenseHat()
sense.set_rotation(180)

batch_data= []

last_alarm = ALARM_FREQUENCY
last_display = DISPLAY_FREQUENCY

if FILENAME == "":
	filename = "SenseLog-"+str(datetime.now())+".csv"
else:
	filename = FILENAME+"-"+str(datetime.now())+".csv"

file_setup(filename)

while True:
	sense_data = get_sense_data()
##	print(sense_data)
	log_data()

	if len(batch_data) >= WRITE_FREQUENCY:
		print("Writing to file..")
		with open(filename,"a") as f:
			for line in batch_data:
				f.write(line + "\n")
			batch_data = []

	current_temp_h = int(round(sense_data[0]))
	current_temp_p = int(round(sense_data[1]))
	current_humidity = int(round(sense_data[2]))

	last_display += 1
	if last_display > DISPLAY_FREQUENCY:
		current_display = "TEMP_H="+str(current_temp_h)+" TEMP_P="+str(current_temp_p)+" HUMIDITY="+str(current_humidity)
		print(current_display)
		sense.show_message(current_display)

##	if last_alarm % 1000 == 0:
##		print(last_alarm)
    
	if current_temp_h < TEMP_H_LOW \
	or current_temp_h > TEMP_H_HIGH \
	or current_temp_p < TEMP_P_LOW \
	or current_temp_p > TEMP_P_HIGH \
	or current_humidity < HUMIDITY_LOW \
	or current_humidity > HUMIDITY_HIGH:
		last_alarm += 1
		if last_alarm > ALARM_FREQUENCY:
			sendemail(from_addr = 'shared@anode.com', 
		        	to_addr_list = ['b1t1l2f5g3r6r7w2@anode.slack.com'],
		          	cc_addr_list = [], 
		         	subject = 'Server Room Environmental Warning', 
		          	message = 'TEMP_H={} TEMP_P={} HUMIDITY={}'.format(current_temp_h,current_temp_p,current_humidity), 
		          	login = 'shared@anode.com', 
		          	password = 'Anode$926!')
			last_alarm = 0
