import socket

class HL7SenderAdapter:
    def send_hl7_message(self):
        message = (
            "MSH|^~\\&|SendingApp|SendingFac|ReceivingApp|ReceivingFac|202505121200||ADT^A01|123456|P|2.3\r"
            "PID|1||123456^^^Hospital^MR||Doe^John||19800101|M\r"
        )

        host = 'localhost'
        port = 2575  # Example port

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.sendall(f"\x0b{message}\x1c\r".encode())  # MLLP framing
                response = s.recv(1024)
                print("HL7 ACK received:\n", response.decode())
        except ConnectionRefusedError:
            print("Unable to connect to HL7 listener.")
