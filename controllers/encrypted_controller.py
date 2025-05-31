import logging
from odoo import http
import logging
import base64

_logger = logging.getLogger(__name__)

SBOX = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
]

RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0x6c, 0x6c, 0x6c, 0x6c, 0x6c]


class WhatsappEncryptedController(http.Controller):

    @staticmethod
    def string_to_bytes(string):
        return [ord(char) for char in string]

    @staticmethod
    def bytes_to_string(byte_array):
        return ''.join(chr(byte) for byte in byte_array)

    @staticmethod
    def xor_arrays(arr1, arr2):
        return [a ^ b for a, b in zip(arr1, arr2)]

    @staticmethod
    def pad_pkcs7(data, block_size=16):
        padding = block_size - (len(data) % block_size)
        return data + [padding] * padding

    @staticmethod
    def unpad_pkcs7(data):
        padding_length = data[-1]
        return data[:-padding_length]

    @staticmethod
    def sub_bytes(state):
        return [SBOX[byte] for byte in state]

    @staticmethod
    def inv_sub_bytes(state):
        INV_SBOX = [0] * 256
        for i in range(256):
            INV_SBOX[SBOX[i]] = i
        return [INV_SBOX[byte] for byte in state]

    @staticmethod
    def shift_rows(state):
        return [
            state[0], state[5], state[10], state[15],
            state[4], state[9], state[14], state[3],
            state[8], state[13], state[2], state[7],
            state[12], state[1], state[6], state[11]
        ]

    @staticmethod
    def inv_shift_rows(state):
        return [
            state[0], state[13], state[10], state[7],
            state[4], state[1], state[14], state[11],
            state[8], state[5], state[2], state[15],
            state[12], state[9], state[6], state[3]
        ]

    @staticmethod
    def mix_columns(state):
        def multiply(a, b):
            result = 0
            for _ in range(8):
                if b & 1:
                    result ^= a
                high_bit = a & 0x80
                a = (a << 1) & 0xFF
                if high_bit:
                    a ^= 0x1B
                b >>= 1
            return result

        result = [0] * 16
        for i in range(4):
            col = state[i * 4:(i + 1) * 4]
            result[i * 4] = multiply(col[0], 2) ^ multiply(col[1], 3) ^ col[2] ^ col[3]
            result[i * 4 + 1] = col[0] ^ multiply(col[1], 2) ^ multiply(col[2], 3) ^ col[3]
            result[i * 4 + 2] = col[0] ^ col[1] ^ multiply(col[2], 2) ^ multiply(col[3], 3)
            result[i * 4 + 3] = multiply(col[0], 3) ^ col[1] ^ col[2] ^ multiply(col[3], 2)
        return result

    @staticmethod
    def inv_mix_columns(state):
        def multiply(a, b):
            result = 0
            for _ in range(8):
                if b & 1:
                    result ^= a
                high_bit = a & 0x80
                a = (a << 1) & 0xFF
                if high_bit:
                    a ^= 0x1B
                b >>= 1
            return result

        result = [0] * 16
        for i in range(4):
            col = state[i * 4:i * 4 + 4]
            result[i * 4] = multiply(col[0], 0x0E) ^ multiply(col[1], 0x0B) ^ multiply(col[2], 0x0D) ^ multiply(col[3], 0x09)
            result[i * 4 + 1] = multiply(col[0], 0x09) ^ multiply(col[1], 0x0E) ^ multiply(col[2], 0x0B) ^ multiply(col[3], 0x0D)
            result[i * 4 + 2] = multiply(col[0], 0x0D) ^ multiply(col[1], 0x09) ^ multiply(col[2], 0x0E) ^ multiply(col[3], 0x0B)
            result[i * 4 + 3] = multiply(col[0], 0x0B) ^ multiply(col[1], 0x0D) ^ multiply(col[2], 0x09) ^ multiply(col[3], 0x0E)
        return result

    @staticmethod
    def key_expansion(key):
        Nk = 6  # Número de palabras de 32 bits en la clave (6 para AES-192)
        Nr = 12 # Número de rondas (12 para AES-192)
        Nb = 4  # Número de columnas en el estado (siempre 4 para AES)

        expanded_key = list(key)
        for i in range(Nk, Nb * (Nr + 1)):
            temp = expanded_key[(i - 1) * 4:i * 4]

            if i % Nk == 0:
                temp = [
                    SBOX[temp[1]] ^ RCON[(i // Nk) - 1],
                    SBOX[temp[2]],
                    SBOX[temp[3]],
                    SBOX[temp[0]]
                ]
            elif i % Nk == 4:
                temp = [SBOX[byte] for byte in temp]

            prev_key = expanded_key[(i - Nk) * 4:(i - Nk + 1) * 4]
            expanded_key += WhatsappEncryptedController.xor_arrays(prev_key, temp)

        return expanded_key
    @staticmethod
    def aes_encrypt(block, expanded_key):
        state = list(block)
        Nr = 12
        state = WhatsappEncryptedController.xor_arrays(state, expanded_key[:16])
        for round in range(1, Nr):
            state = WhatsappEncryptedController.sub_bytes(state)
            state = WhatsappEncryptedController.shift_rows(state)
            state = WhatsappEncryptedController.mix_columns(state)
            state = WhatsappEncryptedController.xor_arrays(
                state, expanded_key[round * 16:(round + 1) * 16]
            )
        state = WhatsappEncryptedController.sub_bytes(state)
        state = WhatsappEncryptedController.shift_rows(state)
        state = WhatsappEncryptedController.xor_arrays(
            state, expanded_key[Nr * 16:(Nr + 1) * 16]
        )
        return state

    @staticmethod
    def aes_decrypt(block, expanded_key):
        state = list(block)
        Nr = 12
        state = WhatsappEncryptedController.xor_arrays(
            state, expanded_key[Nr * 16:(Nr + 1) * 16]
        )
        state = WhatsappEncryptedController.inv_shift_rows(state)
        state = WhatsappEncryptedController.inv_sub_bytes(state)
        for round in range(Nr - 1, 0, -1):
            state = WhatsappEncryptedController.xor_arrays(
                state, expanded_key[round * 16:(round + 1) * 16]
            )
            state = WhatsappEncryptedController.inv_mix_columns(state)
            state = WhatsappEncryptedController.inv_shift_rows(state)
            state = WhatsappEncryptedController.inv_sub_bytes(state)
        state = WhatsappEncryptedController.xor_arrays(state, expanded_key[:16])
        return state

    @http.route('/aes/encrypt', type='json', auth='public', methods=['POST'])
    def encrypt(self, text):
        key = 'Nigga&Lopez&Mora'
        text_bytes = WhatsappEncryptedController.pad_pkcs7(
            WhatsappEncryptedController.string_to_bytes(text)
        )
        key_bytes = WhatsappEncryptedController.string_to_bytes(key.ljust(24, '\0'))[:24]
        expanded_key = WhatsappEncryptedController.key_expansion(key_bytes)
        encrypted_blocks = []
        for i in range(0, len(text_bytes), 16):
            block = text_bytes[i:i + 16]
            encrypted_block = WhatsappEncryptedController.aes_encrypt(block, expanded_key)
            encrypted_blocks.extend(encrypted_block)
        encrypted_text = base64.b64encode(bytes(encrypted_blocks)).decode('utf-8')
        return {'encrypted_text': encrypted_text}

    @staticmethod
    def decrypt_aes_192_with_last_char(encrypted_text):
        try:
            key = "Nigga&Lopez&Mora"

            added_suffix_length = 3  
            _logger.info(f"Longitud esperada de la cadena adicional: {added_suffix_length}")

            encrypted_text_with_suffix = encrypted_text
            _logger.info(f"Cadena encriptada recibida: {encrypted_text_with_suffix}")

            additional_suffix = encrypted_text_with_suffix[-added_suffix_length:]
            _logger.info(f"Cadena adicional extraída: {additional_suffix}")

            encrypted_text_without_suffix = encrypted_text_with_suffix[:-added_suffix_length]
            _logger.info(f"Cadena encriptada sin la parte adicional: {encrypted_text_without_suffix}")

            encrypted_bytes = list(base64.b64decode(encrypted_text_without_suffix))
            _logger.info(f"Bytes encriptados recibidos: {encrypted_bytes}")

            key_bytes = WhatsappEncryptedController.string_to_bytes(key.ljust(24, '\0'))[:24]
            expanded_key = WhatsappEncryptedController.key_expansion(key_bytes)

            decrypted_blocks = []
            for i in range(0, len(encrypted_bytes), 16):
                block = encrypted_bytes[i:i + 16]
                decrypted_block = WhatsappEncryptedController.aes_decrypt(block, expanded_key)
                decrypted_blocks.extend(decrypted_block)

            decrypted_text = WhatsappEncryptedController.bytes_to_string(
                WhatsappEncryptedController.unpad_pkcs7(decrypted_blocks)
            )
            _logger.info(f"Texto desencriptado inicial: {decrypted_text}")

            decrypted = decrypted_text
            _logger.info(f"Texto final con la cadena restaurada: {decrypted}")

            return decrypted
        except Exception as e:
            _logger.error(f"Error desencriptando texto: {e}")
            return None

    @staticmethod
    def decrypt_aes_192(encrypted_text):
        try:
            key = "Nigga&Lopez&Mora"

            # Decodificar el texto cifrado desde base64
            encrypted_bytes = list(base64.b64decode(encrypted_text))
            # Convertir la clave en bytes y expandirla para AES-192
            key_bytes = WhatsappEncryptedController.string_to_bytes(key.ljust(24, '\0'))[:24]
            expanded_key = WhatsappEncryptedController.key_expansion(key_bytes)

            decrypted_blocks = []
            for i in range(0, len(encrypted_bytes), 16):
                block = encrypted_bytes[i:i + 16]
                decrypted_block = WhatsappEncryptedController.aes_decrypt(block, expanded_key)
                decrypted_blocks.extend(decrypted_block)

            # Quitar el padding PKCS#7 y convertir a texto
            decrypted_text = WhatsappEncryptedController.bytes_to_string(
                WhatsappEncryptedController.unpad_pkcs7(decrypted_blocks)
            )

            return decrypted_text
        except Exception as e:
            _logger.error(f"Error desencriptando texto: {e}")
            return None

    @staticmethod
    def decrypt_aes_192_body(encrypted_text):
        try:
            key = "Nigga&Lopez&Mora"

            # Decodificar el texto cifrado desde base64
            encrypted_bytes = list(base64.b64decode(encrypted_text))
            # Convertir la clave en bytes y expandirla para AES-192
            key_bytes = WhatsappEncryptedController.string_to_bytes(key.ljust(24, '\0'))[:24]
            expanded_key = WhatsappEncryptedController.key_expansion(key_bytes)

            decrypted_blocks = []
            for i in range(0, len(encrypted_bytes), 16):
                block = encrypted_bytes[i:i + 16]
                decrypted_block = WhatsappEncryptedController.aes_decrypt(block, expanded_key)
                decrypted_blocks.extend(decrypted_block)

            # Quitar el padding PKCS#7 y convertir a texto
            decrypted_text = WhatsappEncryptedController.bytes_to_string(
                WhatsappEncryptedController.unpad_pkcs7(decrypted_blocks)
            )

            added_suffix_length = 3  
            encrypted_text_with_suffix = decrypted_text
            additional_suffix = encrypted_text_with_suffix[-added_suffix_length:]
            encrypted_text_without_suffix = encrypted_text_with_suffix[:-added_suffix_length]

            return encrypted_text_without_suffix
        except Exception as e:
            _logger.error(f"Error desencriptando texto: {e}")
            return None

    @http.route('/aes/decrypt', type='json', auth='public', methods=['POST'])
    def decrypt(self, encrypted_text):
        key = 'Nigga&Lopez&Mora'
        encrypted_bytes = list(base64.b64decode(encrypted_text))
        key_bytes = WhatsappEncryptedController.string_to_bytes(key.ljust(24, '\0'))[:24]
        expanded_key = WhatsappEncryptedController.key_expansion(key_bytes)
        decrypted_blocks = []
        for i in range(0, len(encrypted_bytes), 16):
            block = encrypted_bytes[i:i + 16]
            decrypted_block = WhatsappEncryptedController.aes_decrypt(block, expanded_key)
            decrypted_blocks.extend(decrypted_block)
        decrypted_text = WhatsappEncryptedController.bytes_to_string(
            WhatsappEncryptedController.unpad_pkcs7(decrypted_blocks)
        )
        return {'decrypted_text': decrypted_text}