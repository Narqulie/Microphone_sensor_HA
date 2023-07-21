# Import necessary libraries
import sounddevice as sd
import numpy as np
import time
import paho.mqtt.client as mqtt
import logging
import json

# Set up Logging
logging.basicConfig(filename="mic_sensor.log",
                    level=logging.INFO,
                    format="%(asctime)s -- %(message)s")

# Load the configuration file
with open("config.json") as config_file:
    config = json.load(config_file)

# Set up MQTT client
logging.info("Reading config for MQTT details:")
broker_address = config["broker_address"]
broker_port = config["broker_port"]
username = config["username"]
password = config["password"]
topic = config["topic"]

logging.info("Setting up MQTT Client")
client = mqtt.Client()
client.username_pw_set(username, password)
client.connect(broker_address, broker_port)
logging.info(
    f"Broker address: {broker_address}, "
    f"port: {broker_port}, "
    f"topic: {topic}"
)


# Setting up the microphone; this is optional, system default is used
def choose_mic():
    devices = sd.query_devices()
    for device in devices:
        if device['max_input_channels'] > 0:  # this is an input device
            logging.info(f"Device #{device['index']}: {device['name']}")
            print(f"Device #{device['index']}: {device['name']}")
    global device_index
    device_index = int(input("Which device should be used for measurements? (enter device number) : "))
    logging.info(f"Input device #{device_index} chosen")


# Define some constants
average_duration = 5  # Duration (in seconds) over which to calculate the average RMS
threshold_factor = 1.5  # Factor to multiply the average RMS to calculate the threshold
sample_rate = 44100  # Sample rate for audio recording
block_size = 1024  # Block size for audio recording
rms_values = []  # List to store recent RMS values
threshold = 0  # Initial threshold value
last_measurement_time = 0  # Time when the last measurement was made


# Define the callback function for audio recording
def audio_callback(indata, frames, time_info, status):
    global threshold, last_measurement_time
    rms = np.sqrt(np.mean(np.square(indata)))  # Calculate the RMS of the audio data
    rms = round(rms, 3)
    rms_values.append(rms)  # Add the RMS to the list of recent RMS values

    # If enough time has passed to calculate a new average RMS and threshold...
    if len(rms_values) >= average_duration * sample_rate / block_size:
        logging.info("Setting new threshold: ")
        average_rms = np.mean(rms_values)  # Calculate the average RMS
        threshold = average_rms * threshold_factor  # Calculate the new threshold
        threshold = round(threshold, 3)
        logging.info(f"New threshold : {threshold}")
        rms_values.clear()  # Clear the list of recent RMS values

    # If enough time has passed to make a new measurement...
    if time.time() - last_measurement_time >= 1:
        last_measurement_time = time.time()  # Update the time of the last measurement
        if rms > threshold:  # If the RMS is greater than the threshold...
            logging.info(f"Noise detected -- {rms}/{threshold}")
            value = "Noise"  # Set the value to be published to the MQTT topic
        else:  # If the RMS is not greater than the threshold...
            logging.info(f"Quiet -- {rms}/{threshold}")
            value = "Quiet"  # Set the value to be published to the MQTT topic
        client.publish(topic, value)  # Publish the value to the MQTT topic


logging.info("Starting process")

choose_mic()
# Start an audio stream with the callback function
stream = sd.InputStream(callback=audio_callback,
                        device=device_index,
                        channels=1,
                        samplerate=sample_rate,
                        blocksize=block_size)
stream.start()  # Start the audio stream


# Start the MQTT client's loop
client.loop_start()


# Run an infinite loop to keep the script running indefinitely
while True:
    time.sleep(0.1)  # Sleep for a short time to avoid consuming too much CPU
