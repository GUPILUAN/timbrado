"""
Universidad Anáhuac Mayab, Mérida
Ingeniería en tecnologías de la información y negocios digitales

Integrantes:
Luis Angel Gutierrez Pineda
Jhonatan Alexis Ac Meneses
Sergio Sebastian Cano Gonzalez
"""

from models.CFDI import CFDI
from resources.Sello import generar_sello
from resources.Cadena import generar_cadena_original
from resources.Certificado import obtener_certificado_y_numero

cfdi = CFDI()
cfdi.set_emisor(
    rfc="EKU9003173C9", nombre="ESCUELA KEMPER URGATE", regimen_fiscal="601"
)
cfdi.set_receptor(
    rfc="JUFA7608212V6",
    nombre="ADRIANA JUAREZ FERNANDEZ",
    uso_cfdi="G03",
    regimen_fiscal="605",
    domicilio_fiscal="01160",
)

cfdi.agregar_concepto(
    clave_prod_serv="01010101",
    cantidad="1",
    clave_unidad="H87",
    descripcion="Producto de prueba",
    valor_unitario="1000.00",
    importe="1000.00",
    objeto_imp="01",
    impuestos=[
        {
            "Base": "1000.00",
            "Impuesto": "002",
            "TipoFactor": "Tasa",
            "TasaOCuota": "0.160000",
            "Importe": "160.00",
        }
    ],
)
cfdi.agregar_impuesto("1000.00", "002", "Tasa", "0.160000", "160.00")

xml_cfdi = cfdi.generar_xml()
print(xml_cfdi)


key_path = "EmpresaFicticia/EKU9003173C9_20230517223532/Claveprivada_FIEL_EKU9003173C9_20230517_223532.key"
cert_path = "EmpresaFicticia/EKU9003173C9_20230517223532/eku9003173c9.cer"
key_password = "12345678a"
xslt_path = "cadenaoriginal_4_0.xslt"
cadena_original: str = generar_cadena_original(xml_string=xml_cfdi, xslt_path=xslt_path)


nc, cb64 = obtener_certificado_y_numero(cert_path=cert_path)

sello_base64 = generar_sello(
    cadena_original=cadena_original, private_key_path=key_path, password=key_password
)

sello = cfdi.agregar_sello_y_cert(
    sello_base64=sello_base64, numero_certificado=nc, certificado_base64=cb64
)

print(sello)  # Imprime el XML con el sello agregado


import requests
import json

url_auth = "https://services.test.sw.com.mx/v2/security/authenticate"

payload = json.dumps({"user": " usuario@pruebas.com", "password": "contraseña1234"})
headers = {"Content-Type": "application/json"}

response = requests.request("POST", url_auth, headers=headers, data=payload)

res = response.json()
data = res.get("data")
if data:
    token = data.get("token")

else:
    print("No se obtuvo token")
    token = ""

url = "https://services.test.sw.com.mx/v4/cfdi33/stamp/v1"

payload = {}
files = [("xml", ("file", open("cfdi.xml", "rb"), "application/octet-stream"))]
headers = {
    "Authorization": token,
    "customid": "myCustomId",
    "Content-Type": "multipart/form-data",
}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.text)
