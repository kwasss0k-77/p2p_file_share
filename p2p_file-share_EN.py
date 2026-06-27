import os
import socket
import sys

BUFFER_SIZE = 8192

def get_punched_socket(remote_ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    print("Punching NAT tunnel... Sending signals...")
    for _ in range(5):
        sock.sendto(b"PUNCH", (remote_ip, port))
    return sock

def send_file(receiver_ip, port):
    file_path = input("\n[PC1] Enter the full path to the file: ").strip().strip('"').strip("'")
    if not os.path.exists(file_path):
        print("Error: File not found!")
        return

    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    sock = get_punched_socket(receiver_ip, port)
    try:
        metadata = f"{file_name}:{file_size}"
        sock.sendto(metadata.encode('utf-8'), (receiver_ip, port))
        
        sock.settimeout(5.0)
        try:
            data, _ = sock.recvfrom(1024)
            if data.decode('utf-8') != "ACCEPT":
                print("PC2 rejected the file request.")
                return
        except socket.timeout:
            print("Connection timeout from PC2. Tunnel closed.")
            return

        print("File transfer started...")
        with open(file_path, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                sock.sendto(bytes_read, (receiver_ip, port))
                
        print("[SUCCESS] The file has been fully sent!")
        
    except Exception as e:
        print(f"Network error: {e}")
    finally:
        sock.close()

def receive_file(sender_ip, port):
    sock = get_punched_socket(sender_ip, port)
    try:
        print(f"\n[PC2] Waiting for request from {sender_ip} on port {port}...")
        sock.settimeout(15.0)
        
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                if data == b"PUNCH":
                    continue
                metadata = data.decode('utf-8')
                if ":" in metadata:
                    break
            except socket.timeout:
                print("Connection timeout.")
                return

        file_name, file_size = metadata.split(":", 1)
        file_size = int(file_size)
        
        print(f"\nAttention! File request: {file_name} ({round(file_size / (1024*1024), 2)} MB)")
        ans = input("Enter 'y' to accept or 'n' to cancel: ").strip().lower()
        
        if ans == 'y':
            sock.sendto("ACCEPT".encode('utf-8'), (sender_ip, port))
            save_path = os.path.join(os.path.expanduser("~"), "Downloads", file_name)
            print(f"Downloading started. It will be saved in Downloads.")
            
            with open(save_path, "wb") as f:
                bytes_received = 0
                sock.settimeout(7.0)
                while bytes_received < file_size:
                    chunk, _ = sock.recvfrom(BUFFER_SIZE + 100)
                    if not chunk or chunk == b"PUNCH":
                        continue
                    f.write(chunk)
                    bytes_received += len(chunk)
            print("[SUCCESS] The file has been fully received!")
        else:
            sock.sendto("DECLINE".encode('utf-8'), (sender_ip, port))
            print("Cancelled.")
            
    except Exception as e:
        print(f"Error during receiving: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    input_port = input("Enter connection port (default 6006): ").strip()
    input_port = int(input_port) if input_port else 6006

    print("\n1. I want to SEND a file (PC1)")
    print("2. I want to RECEIVE a file (PC2)")
    choice = input("Choose your role (1 or 2): ").strip()
    
    input_ip = input("Enter the external IP address of the second PC: ").strip()
    if not input_ip:
        print("Error: IP address is required!")
        sys.exit()

    if choice == "1":
        send_file(input_ip, input_port)
    elif choice == "2":
        receive_file(input_ip, input_port)
        
    input("\nPress Enter to exit...")
