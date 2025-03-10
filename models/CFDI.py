from typing import Any
from Entity import Person
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
    ) -> None:
        """Crea un cfdi sin receptor, ni emisor, es necesario añadirlos despues

        Args:
            version (str, optional): Version del cdfi. Defaults to "4.0".
            serie (str, optional): serie del cdfi. Defaults to "A".
            folio (str, optional): folio unico. Defaults to "12345".
            fecha (str | None, optional): Fecha, de no ponerse, se hace automatico. Defaults to None.
            exportacion (str, optional): Tipo de exportacion. Defaults to "02".
            forma_pago (str, optional): Forma de pago. Defaults to "01".
            condiciones_pago (str, optional): condiciones del pago. Defaults to "Contado".
            subtotal (str, optional): subtotal. Defaults to "1000.00".
            moneda (str, optional): moneda en el que se realizo el pago. Defaults to "MXN".
            total (str, optional): subtotal mas impuestos. Defaults to "1160.00".
            tipo_comprobante (str, optional): tipo de comprobante. Defaults to "I".
            metodo_pago (str, optional): metodo de pago. Defaults to "PUE".
            lugar_expedicion (str, optional): lugar de expedicion. Defaults to "64000".
        """

        self.version: str = version
        self.serie: str = serie
        self.folio: str = folio
        self.fecha: str = (
            fecha if fecha else datetime.datetime.now().isoformat()[:-7]
        )  # Le quitamos los milisegundos
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

    def set_emisor(self, person_emisor: Person) -> None:
        """Añade el emisor al cfdi

        Args:
            person_emisor (Person): Persona emisora del cfdi
        """

        self.emisor = person_emisor

    def set_receptor(self, person_receptor: Person) -> None:
        """Añade el receptor al cfdi

        Args:
            person_receptor (Person): Persona receptora del cfdi
        """
        self.receptor = person_receptor

    def get_emisor(self) -> dict | None:
        """Obtiene el emisor del cfdi

        Returns:
            dict | None: Datos del emisor en formato dict, si no hay: devuelve None
        """
        if not self.emisor:
            return
        return {
            "Rfc": self.emisor.rfc,
            "Nombre": self.emisor.nombre,
            "RegimenFiscal": self.emisor.regimen_fiscal,
        }

    def get_receptor(self) -> dict | None:
        """Obtiene el receptor del cfdi

        Returns:
            dict | None: Datos del receptor en formato dict, si no hay: devuelve None
        """
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
    ) -> None:
        """Agrega un nuevo concepto al cfdi

        Args:
            clave_prod_serv (str): clave del producto o servicio
            cantidad (str): cantidad del producto o servicio
            clave_unidad (str): clave de la unidad
            descripcion (str): descripcion del producto o servicio
            valor_unitario (str): valor unitario del producto o servicio
            importe (str): importe total
            objeto_imp (str): objeto imp
            impuestos (list | None, optional): impuestos. Defaults to None.
        """
        concepto: dict = {
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

    def agregar_impuesto(
        self,
        base: str,
        impuesto: str,
        tipo_factor: str,
        tasa_o_cuota: str,
        importe: str,
    ) -> None:
        """Agrega los impuestos

        Args:
            base (str): base
            impuesto (str): impuesto
            tipo_factor (str): tipo de impuesto
            tasa_o_cuota (str): tasa o factura
            importe (str): importe
        """

        self.impuestos.append(
            {
                "Base": base,
                "Impuesto": impuesto,
                "TipoFactor": tipo_factor,
                "TasaOCuota": tasa_o_cuota,
                "Importe": importe,
            }
        )

    def generar_xml(self) -> str:
        """Genera el xml y lo guarda en la raiz del programa

        Raises:
            ValueError: Si no aun no se han agregado el receptor o emisor, habrá error

        Returns:
            str: aparte de generar el archivo xml, la funcion regresa el mismo en formato string
        """
        ns: str = "http://www.sat.gob.mx/cfd/4"
        xsi: str = "http://www.w3.org/2001/XMLSchema-instance"
        schema_location: str = (
            "http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd"
        )

        attributes: dict = {
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

        comprobante: Any = etree.Element(
            "{http://www.sat.gob.mx/cfd/4}Comprobante",
            nsmap={"cfdi": ns, "xsi": xsi},
            attrib=attributes,
        )

        e: dict | None = self.get_emisor()
        r: dict | None = self.get_receptor()
        if not e or not r:
            raise ValueError("No se encontraron datos de emisor o receptor")
        emisor: Any = etree.SubElement(
            comprobante, "{http://www.sat.gob.mx/cfd/4}Emisor", **e
        )
        receptor: Any = etree.SubElement(
            comprobante, "{http://www.sat.gob.mx/cfd/4}Receptor", **r
        )

        conceptos: Any = etree.SubElement(
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
            concepto: Any = etree.SubElement(
                conceptos,
                "{http://www.sat.gob.mx/cfd/4}Concepto",
                attrib=concept_dict,
                nsmap=None,
            )

            if c["Impuestos"]:
                impuestos: Any = etree.SubElement(
                    concepto,
                    "{http://www.sat.gob.mx/cfd/4}Impuestos",
                    attrib=None,
                    nsmap=None,
                )
                traslados: Any = etree.SubElement(
                    impuestos,
                    "{http://www.sat.gob.mx/cfd/4}Traslados",
                    attrib=None,
                    nsmap=None,
                )
                for imp in c["Impuestos"]:
                    etree.SubElement(
                        traslados, "{http://www.sat.gob.mx/cfd/4}Traslado", **imp
                    )

        impuestos_globales: Any = etree.SubElement(
            comprobante,
            "{http://www.sat.gob.mx/cfd/4}Impuestos",
            TotalImpuestosTrasladados=str(
                sum(float(i["Importe"]) for i in self.impuestos)
            ),
            attrib=None,
            nsmap=None,
        )
        traslados_globales: Any = etree.SubElement(
            impuestos_globales,
            "{http://www.sat.gob.mx/cfd/4}Traslados",
            attrib=None,
            nsmap=None,
        )
        for imp in self.impuestos:
            etree.SubElement(
                traslados_globales, "{http://www.sat.gob.mx/cfd/4}Traslado", **imp
            )

        tree: Any = etree.ElementTree(comprobante)
        tree.write("cfdi.xml", encoding="UTF-8", xml_declaration=True)
        self.string: str = etree.tostring(comprobante).decode()
        return self.string

    def __str__(self) -> str:
        """Retorna como representacion del cfdi en xml

        Returns:
            str: xml en formato string, devolvera vacio si aun no se ha generado
        """
        return self.string

    def agregar_sello_y_cert(
        self, sello_base64: str, numero_certificado: str, certificado_base64: str
    ) -> str | None:
        """Agrega el sello y certificado

        Args:
            sello_base64 (str): sello en base 64
            numero_certificado (str): numero del certificado
            certificado_base64 (str): certidicado en base 64

        Raises:
            ValueError: En caso de que el formato del xml no coincida

        Returns:
            str | None: Si no existe el sello, regresará None
        """
        if not sello_base64 or len(self.string) == 0:
            return
        # Parsear el XML
        root: Any = etree.fromstring(self.string, parser=None)

        # Buscar la etiqueta <cfdi:Comprobante>
        # Si se encuentra la etiqueta, agregar el sello
        if root.tag == "{http://www.sat.gob.mx/cfd/4}Comprobante":
            root.set("Sello", sello_base64)  # Agregar el sello en Base64
            root.set("NoCertificado", numero_certificado)
            root.set("Certificado", certificado_base64)
        else:
            raise ValueError("No se encontró la etiqueta <cfdi:Comprobante> en el XML.")
        tree: Any = etree.ElementTree(root)
        tree.write("cfdi.xml", encoding="UTF-8", xml_declaration=True)
        # Convertir el XML de vuelta a una cadena
        return etree.tostring(root).decode("utf-8")
