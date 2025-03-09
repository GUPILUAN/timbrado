from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import base64


def generar_sello(cadena_original: str, private_key_path: str, password: str):
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_der_private_key(
            key_file.read(),
            password=password.encode() if password else None,
            backend=default_backend(),
        )

    sello = private_key.sign(  # type: ignore
        cadena_original.encode(), padding.PKCS1v15(), hashes.SHA256()  # type: ignore
    )

    return base64.b64encode(sello).decode()
