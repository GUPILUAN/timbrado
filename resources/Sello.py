from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import base64


def generar_sello(
    cadena_original: str, private_key_path: str, password: str | None = None
) -> str:
    """Genera un sello dado un archivo .key

    Args:
        cadena_original (str): cadena original dada por el SAT
        private_key_path (str): path donde se encuentra guardado el archivo .key (clave privada)
        password (str | None, optional): Si el archivo .key tiene contraseña, se debe proporcionar. Defaults to None.

    Returns:
        str: Sello en string
    """

    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_der_private_key(
            key_file.read(),
            password=password.encode() if password else None,
            backend=default_backend(),
        )

    sello: bytes = private_key.sign(  # type: ignore
        cadena_original.encode(), padding.PKCS1v15(), hashes.SHA256()  # type: ignore
    )

    return base64.b64encode(sello).decode()
