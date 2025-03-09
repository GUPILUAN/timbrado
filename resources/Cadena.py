from lxml import etree


def generar_cadena_original(xml_string, xslt_path):
    xml = etree.fromstring(xml_string, parser=None)
    xslt = etree.parse(xslt_path, parser=None)
    transform = etree.XSLT(xslt)
    cadena_original = str(transform(xml))
    return cadena_original.strip()
