"""
Universidad Anáhuac Mayab, Mérida
Ingeniería en tecnologías de la información y negocios digitales

Integrantes:
Luis Angel Gutierrez Pineda
Jhonatan Alexis Ac Meneses
Sergio Sebastian Cano Gonzalez
"""

from models.CFDI import CFDI
from models.Entity import Person
from resources.Sello import generar_sello
from resources.Cadena import generar_cadena_original
from resources.Certificado import obtener_certificado_y_numero


# Creamos el cfdi
cfdi: CFDI = CFDI()

# Proporcionamos los datos del emisor
datos_emisor: dict = {
    "nombre": "ESCUELA KEMPER URGATE",
    "rfc": "EKU9003173C9",
    "regimen_fiscal": "601",
    "domicilio_fiscal": "42501",
}

# Lo convertimos a una Persona y se la agregamos al cfdi
emisor: Person = Person(**datos_emisor)
cfdi.set_emisor(person_emisor=emisor)

# Proporcionamos los datos del receptor
datos_receptor: dict = {
    "nombre": "ADRIANA JUAREZ FERNANDEZ",
    "rfc": "JUFA7608212V6",
    "regimen_fiscal": "605",
    "domicilio_fiscal": "01160",
    "uso_cfdi": "G03",
}

# Lo convertimos a una Persona y se la agregamos al cfdi
receptor: Person = Person(**datos_receptor)
cfdi.set_receptor(person_receptor=receptor)

# Agregamos el concepto
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

# Agreamos el impuesto
cfdi.agregar_impuesto("1000.00", "002", "Tasa", "0.160000", "160.00")

# Generamos el xml
xml_cfdi: str = cfdi.generar_xml()
print(xml_cfdi)


# Con nuestros datos de prueba, como las llaves y certificados vamos a sellar el xml

# Paths al archivo .key y archivo .cer
key_path: str = (
    "EmpresaFicticia/EKU9003173C9_20230517223532/Claveprivada_FIEL_EKU9003173C9_20230517_223532.key"
)
cert_path: str = "EmpresaFicticia/EKU9003173C9_20230517223532/eku9003173c9.cer"
# Password de la llave privada
key_password: str = "12345678a"
# path de la cadena original proporcionada por el SAT
xslt_path: str = "cadenaoriginal_4_0.xslt"
# Generamos la cadena original en str
cadena_original: str = generar_cadena_original(xml_string=xml_cfdi, xslt_path=xslt_path)

# Obtenemos el numero de certificado y el mismo en base 64
nc, cb64 = obtener_certificado_y_numero(cert_path=cert_path)

# Generamos el sello con la cadena original, y la llave privada
sello_base64: str = generar_sello(
    cadena_original=cadena_original, private_key_path=key_path, password=key_password
)

# Con el sello, sellamos el xml cfdi
sello: str | None = cfdi.agregar_sello_y_cert(
    sello_base64=sello_base64, numero_certificado=nc, certificado_base64=cb64
)

print(sello)  # Imprime el XML con el sello agregado


# Ahora acudiremos a la PAC para el timbrado del cfdi sellado
from typing import Any
from requests import Response, request
import json


# url de la api, autorizacion
url_auth: str = "https://services.test.sw.com.mx/v2/security/authenticate"

# Payload: Usuario y contraseña
payload: str | dict = json.dumps(
    {"user": " usuario@pruebas.com", "password": "contraseña1234"}
)
headers: dict = {"Content-Type": "application/json"}

response: Response = request("POST", url_auth, headers=headers, data=payload)

res: dict | None = response.json()
if res is not None:
    data: dict | None = res.get("data")
else:
    data = None
if data:
    token: str | None = data.get("token")
else:
    print("No se obtuvo token")
    token = ""

# url de la api, timbrado
url: str = "https://services.test.sw.com.mx/v4/cfdi33/stamp/v4"

payload = {}
# xml que continene el cfdi sellado
files: list = [("xml", ("file", open("cfdi.xml", "rb"), "application/octet-stream"))]
headers = {
    "Authorization": token,
    "customid": "myCustomId",
    "Content-Type": "multipart/form-data",
}

# lo subimos y esperamos respuesta
response: Response = request("POST", url, headers=headers, data=payload, files=files)

# respuesta del servidor
print(response.text)
