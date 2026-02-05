# procesar_xml.py

from lxml import etree

def leer_factura_xml(ruta_xml):
    tree = etree.parse(ruta_xml)
    root = tree.getroot()

    ns = {'ns': root.nsmap[None]}

    datos = {
        "fecha": root.findtext(".//ns:fechaEmision", namespaces=ns),
        "razon_social": root.findtext(".//ns:razonSocial", namespaces=ns),
        "ruc": root.findtext(".//ns:ruc", namespaces=ns),
        "subtotal": root.findtext(".//ns:totalSinImpuestos", namespaces=ns),
        "total": root.findtext(".//ns:importeTotal", namespaces=ns)
    }

    # IVA (si existe)
    iva = root.findall(".//ns:totalImpuesto/ns:valor", namespaces=ns)
    datos["iva"] = iva[0].text if iva else "0.00"

    return datos
