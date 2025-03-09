from .Entity import Person
from lxml import etree
import datetime


class CFDI:

    def __init__(
        self,
        version: str = "4.0",
        serie: str = "A",
        folio: str = "12345",
        fecha: str | None = None,
        exportacion: str = "02",
        forma_pago: str = "01",
        condiciones_pago: str = "Contado",
        subtotal: str = "1000.00",
        moneda: str = "MXN",
        total: str = "1160.00",
        tipo_comprobante: str = "I",
        metodo_pago: str = "PUE",
        lugar_expedicion: str = "64000",
    ):

        self.version: str = version
        self.serie: str = serie
        self.folio: str = folio
        self.fecha: str = fecha if fecha else datetime.datetime.now().isoformat()[:-7]
        self.exportacion: str = exportacion
        self.forma_pago: str = forma_pago
        self.condiciones_pago: str = condiciones_pago
        self.subtotal: str = subtotal
        self.moneda: str = moneda
        self.total: str = total
        self.tipo_comprobante: str = tipo_comprobante
        self.metodo_pago: str = metodo_pago
        self.lugar_expedicion: str = lugar_expedicion

        self.emisor: Person | None = None
        self.receptor: Person | None = None
        self.conceptos: list = []
        self.impuestos: list = []

        self.string: str = ""

    def set_emisor(self, rfc: str, nombre: str, regimen_fiscal: str) -> None:
        self.emisor = Person(rfc=rfc, nombre=nombre, regimen_fiscal=regimen_fiscal)

    def set_receptor(
        self,
        rfc: str,
        nombre: str,
        uso_cfdi: str,
        regimen_fiscal: str,
        domicilio_fiscal: str,
    ):
        self.receptor = Person(
            rfc=rfc,
            nombre=nombre,
            uso_cfdi=uso_cfdi,
            regimen_fiscal=regimen_fiscal,
            domicilio_fiscal=domicilio_fiscal,
        )

    def get_emisor(self) -> dict | None:
        if not self.emisor:
            return
        return {
            "Rfc": self.emisor.rfc,
            "Nombre": self.emisor.nombre,
            "RegimenFiscal": self.emisor.regimen_fiscal,
        }

    def get_receptor(self) -> dict | None:
        if not self.receptor:
            return
        return {
            "Rfc": self.receptor.rfc,
            "Nombre": self.receptor.nombre,
            "UsoCFDI": self.receptor.uso_cfdi,
            "RegimenFiscalReceptor": self.receptor.regimen_fiscal,
            "DomicilioFiscalReceptor": self.receptor.domicilio_fiscal,
        }

    def agregar_concepto(
        self,
        clave_prod_serv: str,
        cantidad: str,
        clave_unidad: str,
        descripcion: str,
        valor_unitario: str,
        importe: str,
        objeto_imp: str,
        impuestos: list | None = None,
    ):
        concepto = {
            "ClaveProdServ": clave_prod_serv,
            "Cantidad": cantidad,
            "ClaveUnidad": clave_unidad,
            "Descripcion": descripcion,
            "ValorUnitario": valor_unitario,
            "Importe": importe,
            "ObjetoImp": objeto_imp,
            "Impuestos": impuestos if impuestos else [],
        }
        self.conceptos.append(concepto)

    def agregar_impuesto(self, base, impuesto, tipo_factor, tasa_o_cuota, importe):
        self.impuestos.append(
            {
                "Base": base,
                "Impuesto": impuesto,
                "TipoFactor": tipo_factor,
                "TasaOCuota": tasa_o_cuota,
                "Importe": importe,
            }
        )

    def generar_xml(self):
        ns = "http://www.sat.gob.mx/cfd/4"
        xsi = "http://www.w3.org/2001/XMLSchema-instance"
        schema_location = "http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd"

        attributes = {
            "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": schema_location,
            "Version": self.version,
            "Serie": self.serie,
            "Folio": self.folio,
            "Fecha": self.fecha,
            "FormaPago": self.forma_pago,
            "Exportacion": self.exportacion,
            "CondicionesDePago": self.condiciones_pago,
            "SubTotal": self.subtotal,
            "Moneda": self.moneda,
            "Total": self.total,
            "TipoDeComprobante": self.tipo_comprobante,
            "MetodoPago": self.metodo_pago,
            "LugarExpedicion": self.lugar_expedicion,
        }

        comprobante = etree.Element(
            "{http://www.sat.gob.mx/cfd/4}Comprobante",
            nsmap={"cfdi": ns, "xsi": xsi},
            attrib=attributes,
        )

        e = self.get_emisor()
        r = self.get_receptor()
        if not e or not r:
            raise ValueError("No se encontraron datos de emisor o receptor")
        emisor = etree.SubElement(
            comprobante, "{http://www.sat.gob.mx/cfd/4}Emisor", **e
        )
        receptor = etree.SubElement(
            comprobante, "{http://www.sat.gob.mx/cfd/4}Receptor", **r
        )

        conceptos = etree.SubElement(
            comprobante,
            "{http://www.sat.gob.mx/cfd/4}Conceptos",
            nsmap=None,
            attrib=None,
        )
        for c in self.conceptos:
            concept_dict: dict = {
                "ClaveProdServ": c["ClaveProdServ"],
                "Cantidad": c["Cantidad"],
                "ClaveUnidad": c["ClaveUnidad"],
                "Descripcion": c["Descripcion"],
                "ValorUnitario": c["ValorUnitario"],
                "ObjetoImp": c["ObjetoImp"],
                "Importe": c["Importe"],
            }
            concepto = etree.SubElement(
                conceptos,
                "{http://www.sat.gob.mx/cfd/4}Concepto",
                attrib=concept_dict,
                nsmap=None,
            )

            if c["Impuestos"]:
                impuestos = etree.SubElement(
                    concepto,
                    "{http://www.sat.gob.mx/cfd/4}Impuestos",
                    attrib=None,
                    nsmap=None,
                )
                traslados = etree.SubElement(
                    impuestos,
                    "{http://www.sat.gob.mx/cfd/4}Traslados",
                    attrib=None,
                    nsmap=None,
                )
                for imp in c["Impuestos"]:
                    etree.SubElement(
                        traslados, "{http://www.sat.gob.mx/cfd/4}Traslado", **imp
                    )

        impuestos_globales = etree.SubElement(
            comprobante,
            "{http://www.sat.gob.mx/cfd/4}Impuestos",
            TotalImpuestosTrasladados=str(
                sum(float(i["Importe"]) for i in self.impuestos)
            ),
            attrib=None,
            nsmap=None,
        )
        traslados_globales = etree.SubElement(
            impuestos_globales,
            "{http://www.sat.gob.mx/cfd/4}Traslados",
            attrib=None,
            nsmap=None,
        )
        for imp in self.impuestos:
            etree.SubElement(
                traslados_globales, "{http://www.sat.gob.mx/cfd/4}Traslado", **imp
            )

        tree = etree.ElementTree(comprobante)
        tree.write("cfdi.xml", encoding="UTF-8", xml_declaration=True)
        self.string: str = etree.tostring(comprobante).decode()
        return self.string

    def __str__(self) -> str:
        return self.string

    def agregar_sello_y_cert(
        self, sello_base64: str, numero_certificado, certificado_base64
    ) -> str | None:
        if not sello_base64 or len(self.string) == 0:
            return
        # Parsear el XML
        root = etree.fromstring(self.string, parser=None)

        # Buscar la etiqueta <cfdi:Comprobante>
        # Si se encuentra la etiqueta, agregar el sello
        if root.tag == "{http://www.sat.gob.mx/cfd/4}Comprobante":
            root.set("Sello", sello_base64)  # Agregar el sello en Base64
            root.set("NoCertificado", numero_certificado)
            root.set("Certificado", certificado_base64)
        else:
            raise ValueError("No se encontró la etiqueta <cfdi:Comprobante> en el XML.")
        tree = etree.ElementTree(root)
        tree.write("cfdi.xml", encoding="UTF-8", xml_declaration=True)
        # Convertir el XML de vuelta a una cadena
        return etree.tostring(root).decode("utf-8")
