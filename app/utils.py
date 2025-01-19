from cryptography.fernet import Fernet

# Encryption key (must be securely stored for future use)
encryption_key = Fernet.generate_key()
fernet = Fernet(encryption_key)

def encrypt_data(data: str) -> str:
    """Encrypts the input data."""
    if data is None:
        return None
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(data: str) -> str:
    """Decrypts the input data."""
    if data is None:
        return None
    return fernet.decrypt(data.encode()).decode()
