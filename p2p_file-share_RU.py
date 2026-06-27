import os
import socket
import sys

BUFFER_SIZE = 8192

def get_punched_socket(remote_ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    print("Пробивка туннеля через NAT... Отправка сигналов...")
    for _ in range(5):
        sock.sendto(b"PUNCH", (remote_ip, port))
    return sock

def send_file(receiver_ip, port):
    file_path = input("\n[ПК1] Введите полный путь к файлу: ").strip().strip('"').strip("'")
    if not os.path.exists(file_path):
        print("Ошибка: Файл не найден!")
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
                print("ПК2 отклонил прием файла.")
                return
        except socket.timeout:
            print("Превышено время ожидания ответа от ПК2. Туннель закрыт.")
            return

        print("Передача файла началась...")
        with open(file_path, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                sock.sendto(bytes_read, (receiver_ip, port))
                
        print("[УСПЕХ] Файл полностью отправлен!")
        
    except Exception as e:
        print(f"Ошибка сети: {e}")
    finally:
        sock.close()

def receive_file(sender_ip, port):
    sock = get_punched_socket(sender_ip, port)
    try:
        print(f"\n[ПК2] Ожидание запроса от {sender_ip} на порту {port}...")
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
                print("Время ожидания подключения истекло.")
                return

        file_name, file_size = metadata.split(":", 1)
        file_size = int(file_size)
        
        print(f"\nВнимание! Запрос на файл: {file_name} ({round(file_size / (1024*1024), 2)} МБ)")
        ans = input("Нажмите 'y' чтобы принять, или 'n' для отмены: ").strip().lower()
        
        if ans == 'y':
            sock.sendto("ACCEPT".encode('utf-8'), (sender_ip, port))
            save_path = os.path.join(os.path.expanduser("~"), "Downloads", file_name)
            print(f"Прием начался. Файл сохранится в Загрузки.")
            
            with open(save_path, "wb") as f:
                bytes_received = 0
                sock.settimeout(7.0)
                while bytes_received < file_size:
                    chunk, _ = sock.recvfrom(BUFFER_SIZE + 100)
                    if not chunk or chunk == b"PUNCH":
                        continue
                    f.write(chunk)
                    bytes_received += len(chunk)
            print("[УСПЕХ] Файл полностью получен!")
        else:
            sock.sendto("DECLINE".encode('utf-8'), (sender_ip, port))
            print("Отказ от приема.")
            
    except Exception as e:
        print(f"Ошибка при приеме: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    input_port = input("Введите порт подключения (по умолчанию 6006): ").strip()
    input_port = int(input_port) if input_port else 6006

    print("\n1. Я хочу ОТПРАВИТЬ файл (ПК1)")
    print("2. Я хочу ПРИНЯТЬ файл (ПК2)")
    choice = input("Выберите роль (1 или 2): ").strip()
    
    input_ip = input("Введите внешний IP-адрес второго компьютера: ").strip()
    if not input_ip:
        print("Ошибка: IP-адрес обязателен для связи!")
        sys.exit()

    if choice == "1":
        send_file(input_ip, input_port)
    elif choice == "2":
        receive_file(input_ip, input_port)
        
    input("\nНажмите Enter для выхода...")
