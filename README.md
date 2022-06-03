# wav_via_udp

The project allows sending audio from client to server. The audio transfer is made via UDP, TCP is used for the 'client's stream' port separation.
Files are saved on server side in *.wav format   


## Installation

Clone the project.

## Usage

To run client use:

```python3 client.py --host <server_hostname>```

(use 127.0.0.1 if the server is running on the same local machine)

use -ff key to indicate the path to the wav file you want to transfer

```python3 client.py --host <server_hostname> -ff <path_to_file>```

use -fr key to send the 5-seconds record from mic instead of file

```python3 client.py --host <server_hostname> -fr```  


For audio from file "test.wav" file will be used by default




To run server use:

python3 server.py

