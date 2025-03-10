from lxml import etree
from typing import Any


def generar_cadena_original(xml_string: str, xslt_path: str) -> str:
    """Dada la cadena original obtenida del SAT, esta funcion devuelve el str de dicha cadena

    Args:
        xml_string (str): el xml cdfi
        xslt_path (str): path donde se encuentra guardada la cadena original

    Returns:
        str: cadena original transformada
    """
    xml: Any = etree.fromstring(xml_string, parser=None)
    xslt: Any = etree.parse(xslt_path, parser=None)
    transform: etree.XSLT = etree.XSLT(xslt)
    cadena_original: str = str(transform(xml))
    return cadena_original.strip()
