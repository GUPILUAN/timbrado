import base64


def obtener_certificado_y_numero(cert_path: str) -> tuple[str, str]:
    """Obtiene el numero de certificado y el certificado en base 64 de un archivo .cer

    Args:
        cert_path (str): path donde se encuentra guardado el certificado

    Returns:
        tuple[str, str]: numero de certificado y certificado en base 64
    """
    from cryptography.x509 import load_der_x509_certificate

    with open(cert_path, "rb") as f:
        cert_data: bytes = f.read()

    cert = load_der_x509_certificate(cert_data)
    numero_certificado: str = hex(cert.serial_number)[2:22].upper()

    certificado_base64: str = base64.b64encode(cert_data).decode("utf-8")

    return numero_certificado, certificado_base64
