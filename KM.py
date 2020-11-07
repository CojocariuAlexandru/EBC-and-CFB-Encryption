from Crypto.Cipher import AES
import os

# Cheia cu care KM cripteaza cheile generate
key = b'abcdefghiiiiiiiq'

# KM este un server - ofera o cheie generata random cand i se cere
def generate_new_key():
    cipher = AES.new(key)
    return cipher.encrypt(os.urandom(16))

import socket

# Deschid serverul la portul 3000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Comunicare TCP IPv4
s.bind((socket.gethostname(), 3000))
s.listen(3)

# Intr o bucla infinita astept cereri si furnizez chei
while True:
    clientsocket, adress = s.accept()
    print('Conexiune stabilita!')
    clientsocket.send(bytes(generate_new_key()))
    clientsocket.close()