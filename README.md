# EE-x96-Drone-Traffic-Profiling-Protocol-Reverse-Engineering
This repository is for the EE x96: Drone Security project under Dr. Yingfei Dong at the University of Hawaii at Manoa. 

See last year's [UAVClassifier](https://github.com/marionne/uav-classifier)


# DataParser
Running main.py will parse and plot all the JSON in the specified directory

### How this all works
This script parses through given JSON file from Decrypted/ and extracts the payload data for each packet.
  
This payload data is then parsed using the MAVLINK 2.0 Serialization

Graphs Occurrence by Msg_ID

Finds top 4 most abundant packets and heartbeat and provides:

 - message type via xml parsing

 - count, average size, average time delta

 - graph of MavLink message payload size

 - graph of MavLink message time delta

Outputs to Excel (.xlsx) sheet in Results/ directory

### Setup
From Team Drive,
  1) Download pcap from OFFICIAL DATA folder 

Using Wireshark,
   1) Decrypt Packets 
      1) Edit > Preferences > Protocols > IEEE 802.11 > Edit (Decryption Keys)
      2) Create new entry
      3) Add wpa-pwd type   
      4) Under key field, insert password of drone (passwords found in cmdlist.txt in Data folder of team drive)
   2) Filter UDP
   3) Export as JSON
      1) File > Export Packet Dissections > As JSON...
      2) Place all JSON into the 'Decrypted' directory*

Note: the variable json_location specifies the path to this JSON file

*IMPORTANT: Make sure main.py points to the correct location of your JSON files


### How to run
**I recommend Pycharm for convenience.** This was developed in JetBrains PyCharm 2019.1.2

    Set script path to main.py

With Anaconda Prompt,
```
# uncomment src modules in data_parser.py
# perform update if prompted
    > python3 -m pip install --upgrade pip --user
# install required libraries
    > python3 -m pip install pandas --user
    > python3 -m pip install openpyxl --user
    > python3 -m pip install xlsxwriter --user
    > python3 -m pip install [LIBRARY] --user
# clone repo --> enter main directory containing main.py
    > git clone [LINK]
    > cd [DIRECTORY]
# Specify filepath for JSON files in main.py --> execute script
    > python3 .\main.py
``` 
       
### Work in Progress
- normal distribution plot for each message id
- overlay distribution plots for each message id of given drone





