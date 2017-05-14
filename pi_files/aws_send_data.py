'''
/*
 * Copyright 2010-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''
"""
/*
* Aurelio Arango
* CS697 Raspeberry Pi Board
* Collect data from MBED microcontroller via serial
* Then, send data to AWS server
* Use, AMazons basicPubSub 
*/
"""
import serial
from time import gmtime, strftime

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import sys
import logging
import time
import getopt

# Custom MQTT message callback
def customCallback(client, userdata, message):
	print("Received a new message: ")
	print(message.payload)
	print("from topic: ")
	print(message.topic)
	print("--------------\n\n")


# Read in command-line parameters
useWebsocket = False
host = "a2tw4b1e0sk2cq.iot.us-west-2.amazonaws.com"
rootCAPath = "/home/pi/deviceSDK/certs/root_ca_oregon_aws.cer"
certificatePath = "/home/pi/deviceSDK/certs/a49d54c41a-certificate.pem.crt"
privateKeyPath = "/home/pi/deviceSDK/certs/a49d54c41a-private.pem.key"

#Base pubsub sample code
# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
	myAWSIoTMQTTClient = AWSIoTMQTTClient("MyPiAA", useWebsocket=True)
	myAWSIoTMQTTClient.configureEndpoint(host, 443)
	myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
	myAWSIoTMQTTClient = AWSIoTMQTTClient("MyPiAA")
	myAWSIoTMQTTClient.configureEndpoint(host, 8883)
	myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe("MyPiAA", 1, customCallback)
time.sleep(2)

# Publish to the same topic while there is a Serial Connection

try:
    #create serial object
    ser = serial.Serial()
    #set port
    ser.port = '/dev/ttyACM0'
    #open Port
    ser.open()
    
    print "Serial Connection Stablished"
    count=0;
    while ser.isOpen():
    #while count < 20:
        #line reads temperature, humidity and pressure
        #format "Data: temp(f) hum(f) press(f) \r\n"
        print "Start To Read Data"
        line= ser.readline()
        print line
        items= line.split(" ");
        time_value = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        print time_value +"\n"
        if len(items) == 5:
            data = "{\"DateTime\": "+time_value+", \"Temperature\": "+str(items[1])+", \"Humidity\": "+str(items[2])+", \"Pressure\": "+str(items[3])+"}"
        else:
            data = "{\"DateTime\": "+time_value+", \"Temperature\": 0, \"Humidity\": 0, \"Pressure\": 0}"
        #data = json.dumps( dict (DateTime=("2017-05-11"),Temperature=("29"),Humidity=("58"), Pressure=("999") ) )
        print data
        #publish data to server
        myAWSIoTMQTTClient.publish("MyPiAA", data, 1)
        print data
        count+=1;
        
except:
    print "Unable to Open Serial Connection"


