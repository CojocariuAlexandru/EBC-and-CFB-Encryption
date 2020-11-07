from Crypto.Cipher import AES
import socket

init_vector =  'kfjamzngkxmchrqw'


# Similar ca la A, aici avem functiile de decriptare
def decrypt_ECB(encrypted_blocks):
    decrypted_text = ''
    for bloc in encrypted_blocks:
        decrypted_text += make_xor(bloc, key)
    return decrypted_text

def decrypt_CFB(encrypted_blocks):
    decrypted_text = ''
    decrypted_block = make_xor(init_vector, key)
    decrypted_block = make_xor(decrypted_block, encrypted_blocks[0])
    decrypted_text += decrypted_block
    
    for bloc_index in range(1, len(encrypted_blocks)):
        decrypted_block = make_xor(encrypted_blocks[bloc_index-1], key)
        decrypted_block= make_xor(decrypted_block, encrypted_blocks[bloc_index])
        decrypted_text += decrypted_block
        
    return decrypted_text


# Asteapta cheia de la A
def receive_key_from_A():
    global mod_operare
    
    # Stabilesc conexiunea
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #IPv4 TCP communication
    s.bind((socket.gethostname(), 3001))
    s.listen(3)
    clientsocket, adress = s.accept()
    print('Conexiune stabilita!')
    
    # Primesc cheia de criptare si modul de operare
    key_obtained = clientsocket.recv(16)
    mod_operare = clientsocket.recv(1)
    
    if mod_operare == b'\x00':
        print("Mod operare inregistrat: CFB")
    else:
        print("Mod operare inregistrat: ECB")

    s.close()
    return key_obtained

# Notifica pe A sa inceapa transmisia
def start_transmision():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), 3002))
    s.send(bytes('1'))
    print('Am transmis lui A semnal de incepere a transmisiei')
    s.close()
    
# Primeste criptotext-ul de la A
def receive_cryptotext():
    crypto_blocks = []
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostname(), 3001))
    s.listen(3)
    
    # Incep sa primesc cripto-text intr-o bucla infinita
    while True:
        clientsocket, adress = s.accept()
        # Primesc 16 bytes
        crypto_text = clientsocket.recv(30)
        print(crypto_text.decode())
        if crypto_text == b'\x00':
            break
        crypto_blocks.append(crypto_text.decode())
        
    # In functie de modul de operare decriptez si afisez pe ecran
    if mod_operare == b'\x00':
        print(decrypt_CFB(crypto_blocks).rstrip('0'))
    else:
        print(decrypt_ECB(crypto_blocks).rstrip('0'))
    
    s.close()
    
# Functia de criptare aplicata in cadrul algoritmului "invers" pentru a decripta criptotextul
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
        xor_result += chr(val1 ^ val2)
    return xor_result