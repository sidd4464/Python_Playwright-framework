import xml.etree.ElementTree as ET

from parabank_api import _xml_to_dict


def test_xml_parser_supports_repeated_nodes():
    xml = """
    <accounts>
      <account><id>1</id></account>
      <account><id>2</id></account>
    </accounts>
    """
    parsed = _xml_to_dict(ET.fromstring(xml))
    assert "accounts" in parsed
    assert isinstance(parsed["accounts"]["account"], list)
