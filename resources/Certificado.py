import base64


def obtener_certificado_y_numero(cert_path):
    from cryptography.x509 import load_der_x509_certificate

    with open(cert_path, "rb") as f:
        cert_data = f.read()

    cert = load_der_x509_certificate(cert_data)
    numero_certificado = hex(cert.serial_number)[2:22].upper()

    certificado_base64 = base64.b64encode(cert_data).decode("utf-8")

    return numero_certificado, certificado_base64
