<p align="center">
  <img src="src/my_logo.png" alt="logotype" width="200">
</p>

# p2p file share

## What is it?
This program is designed for fast file transfer between two PCs (p2p socket connection), requiring only an internet connection. It's suitable for use in regions with limited internet access or for people without instant messaging apps (or who don't know how to share files with other users).

## Instruction

### Hey-yo! First, download the program from the releases onto the computers you need (2). Then:
1. Check the IP addresses of your PCs. To do this, go to:
   * https://nordvpn.com
   * https://www.myip.com/
   * https://whatismyipaddress.com/
2. Run the file on both computers:
   * **2.1** Enter the port on both PCs (leave it blank and press Enter if you don't know or are unsure)
   * **2.2** Select role: 1 or 2
   * **2.3** If you are the recipient, enter the sender's IP address, or vice versa. ATTENTION! After entering the IP address, you must simultaneously press Enter within half a minute.
   * **2.4** After successfully completing the above steps, the sender must enter the full path to the file (not a folder; if there are many files, simply zip them).
   * **2.5** The recipient, in turn, must wait for the file to be sent and enter "y" if they want to receive it.
3. Wait for the file to be sent, and you're done! The file has been saved to your default "C:/users/user_name/Downloads" folder.

## For developers
The program is also suitable for study and modification, and can also serve as a base for a similar program. The program was compiled using `pyinstaller --clean --onefile --icon=src/my_logo.ico p2p_file-share_EN.py`. Initially, I wanted to use the "aiortc" and "paho-mqtt" libraries, but I got confused and forgot about them. If you want to use them, open a console in the source code folder and type: `pip install -r additionally.txt`.
