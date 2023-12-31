# Microphone Noise Sensor for Home Assistant

This Python script uses a microphone to detect noise levels and sends the noise level status to a MQTT broker. The noise level status can then be used by Home Assistant or any other platform that can subscribe to the MQTT topic.

## Requirements

- Python 3.6+
- sounddevice
- numpy
- paho-mqtt
- An MQTT broker (like Mosquitto)

## Setup

1. Install the necessary Python libraries with pip:

    ```bash
    pip install sounddevice numpy paho-mqtt
    ```

2. Configure the MQTT details (broker address, broker port, and topic) in `config.json`:

    ```json
    {
    "broker_address": "<your_mqtt_broker_ip>",
    "broker_port": "<your_mqtt_broker_port>",
    "topic": "<your_mqtt_topic>",
    "username": "<your_mqtt_username>",
    "password": "<your_mqtt_password>"
    }
    ```
## How It Works

The script records audio from the chosen microphone, calculates the root mean square (RMS) as a measure of the amplitude of the audio, and compares the RMS to a threshold to determine whether the environment is noisy or quiet.

If the RMS is above the threshold, it is considered noisy; otherwise, it is considered quiet. The threshold is recalculated every 5 seconds as 1.5 times the average of the recent RMS values.

The noise level status ("Noise" or "Quiet") is then published to the specified MQTT topic.

All major actions are logged in mic_sensor.log.

Notes:

This script requires access to audio hardware and the network. It won't run in environments where these are not available.

## Run

To run the script, use the command:

```bash
python3 main.py
