# Asymmetric cryptography
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization


class Securuty:
    """Encryption and decryption of data using asymmetric cryptography module"""

    def __init__(self) -> None:
        self.private_key = rsa.generate_private_key(65537, 2048)
        self.public_key = self.private_key.public_key()

    def getSerialized_publicKey(self) -> bytes:
        """Give this to clients for exchange encrypted data"""

        serialized_publicKey = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return serialized_publicKey

    def encrypt(self, message: str, client_publicKey: bytes) -> bytes:
        """Encrypt message using client public key"""

        public_key = serialization.load_pem_public_key(client_publicKey)

        encrypted_message = public_key.encrypt(
            message.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return encrypted_message

    def decrypt(self, encrypted_message: bytes) -> str:
        """Decrypt message using server private key"""

        decrypted_message = self.private_key.decrypt(
            encrypted_message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return decrypted_message.decode()


security = Securuty()
