import socket

hl7_message = "\x0bMSH|^~\\&|SendingApp|SendingFac|ReceivingApp|ReceivingFac|20240513||ADT^A01|123456|P|2.3\rPID|||12345||DOE^JOHN\r\x1c\r"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect(('127.0.0.1', 2575))
        s.sendall(hl7_message.encode('utf-8'))
        ack = s.recv(1024)
        print("✅ ACK received from HL7 listener:\n", ack.decode('utf-8'))
    except Exception as e:
        print("❌ Unable to connect to HL7 listener.", e)
