from Crypto.Cipher import AES
import socket
import time


init_vector =  'kfjamzngkxmchrqw'
mod_operare = 1 # 0 - ECB, 1 - CFB sa zicem ca aleg CFB

# encrypt_ECB() si encrypt_CFB() sunt functiile de criptare pentru cele doua moduri
# Amandoua folosesc functia make_xor() pentru criptare
def encrypt_ECB(text):
    encrypted_blocks = []
    
    # Daca textul nu poate fi impartit in blocuri de 16 bytes mai pun la dreapta caractere
    while len(text) % 16 != 0:
        text = text + '0'
        
    # Separ textul in blocuri de 16 caractere si le criptez pe rand
    for bloc_index in range(0, len(text)//16):
        bloc_text = text[bloc_index*16:(bloc_index+1)*16]
        encrypted_blocks.append(make_xor(bloc_text, key))
        
    # Dupa ce am criptat fiecare bloc returnez lista de blocuri criptate
    return encrypted_blocks

def encrypt_CFB(text):
    encrypted_blocks = []
    
    # Daca textul nu poate fi impartit in blocuri de 16 bytes mai pun la dreapta caractere
    while len(text) % 16 != 0:
        text = text + '0'
        
    # Am urmat instructiunile din schema algoritmului CFB
    cipher_block = make_xor(init_vector, key)
    cipher_block = make_xor(cipher_block, text[0:16])
    encrypted_blocks.append(cipher_block)
    
    for bloc_index in range(1, len(text)//16):
        cipher_block = make_xor(encrypted_blocks[bloc_index-1], key)
        cipher_block = make_xor(cipher_block, text[bloc_index*16:(bloc_index+1)*16])
        encrypted_blocks.append(cipher_block)

    return encrypted_blocks

# Functie creata de mine pentru criptare ca sa nu mai folosesc AES
def make_xor(sir1, sir2):
    xor_result = ''
    for i in range(0, len(sir1)):        
        if type(sir1).__name__ == 'bytes':
            val1 = ord(chr(sir1[i]))
        else:
            val1 = ord(sir1[i])
            
        if type(sir2).__name__ == 'bytes':
            val2 = ord(chr(sir2[i]))
        else:
            val2 = ord(sir2[i])

            
        if type(sir2).__name__ == 'bytes':
            xor_result += chr(val1 ^ val2)
        else:
            xor_result += chr(val1 ^ val2)
    return xor_result

# Functia care face cerere de o cheie catre KM
def make_key_request():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), 3000))
    key_obtained = s.recv(16)
    return key_obtained

# Functia care ii da lui B cheia obtinuta de la KM si modul de operare folosit
def give_key_and_operation_mode_to_B():
    global key
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), 3001))
    key = make_key_request()
    s.send(key)
    s.send(bytes(mod_operare))
    
    s.close()

# Functia care astepta de la B permisiunea de a trimite cripto-text
def wait_confirmation_from_B():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostname(), 3002))
    s.listen(1)
    
    clientsocket, adress = s.accept()
    start_transmisie = clientsocket.recv(1)
    
    s.close()
    
# Criptez textul conform modului de operare ales si incep transmisia catre B
def send_cryptotext_to_B():
    # Criptez in functie de modul de operare ales
    if mod_operare == 0:
        crypted_blocks = encrypt_ECB(text_de_trimis)
    else:
        crypted_blocks = encrypt_CFB(text_de_trimis)
    
    print(crypted_blocks)
        
    # Dupa criptare, trimit blocurile criptate pe rand nodului B, fiecare avand 16 bytes
    for i in range(0, len(crypted_blocks)):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((socket.gethostname(), 3001))
        s.send(crypted_blocks[i].encode())
        s.close()
        time.sleep(0.1)
        
    # La final mai trimit un caracter special pentru a-l notifica pe B ca am finalizat transmisia
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), 3001))
    s.send(bytes('\x00', encoding='utf-8'))
    
    # Dupa trimitere, inchide socket-ul
    s.close()
