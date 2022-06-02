# wav_via_udp

The project allows sending audio from client to server. The audio transfer is made via UDP, TCP is used for the 'client's stream' port separation.
Files are saved on server side in *.wav format   


## Installation

Clone the project.

## Usage

To run client use:

python3 client.py --host <server_hostname>
server_hostname is 127.0.0.1 if the server is running on the same local machine


Please be aware that for audio recording pyaudio is needed.  
For audio from file test wav file is added (and will be used by default) 

To run server use:

python3 server.py

