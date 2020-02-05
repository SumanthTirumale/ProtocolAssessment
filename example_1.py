import unittest
from protocols.ipp.wrapper import IPP


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.host = "192.168.80.78"
        self.ipp = IPP(self.host)

    @staticmethod
    def get_printer_attributes():
        operation_attributes_tag = {
            "attributes-charset": "utf-8",
            "attributes-natural-language": "en-us",
            "printer-uri": "ipp://192.168.80.78/ipp/print",
            "requesting-user-name": "SVA-Automation",
        }

        _get_printer_attributes = {
            "operation-attributes-tag": operation_attributes_tag,
        }

        return _get_printer_attributes

    def test_printer_attributes(self):
        first_line, headers, body = self.ipp.send(
            op_type="Get-Printer-Attributes", version=1.0, **self.get_printer_attributes()
        )

        status_code_actual_value = body['status-code']
        status_code_accepted_value = "successful-ok"

        self.assertEqual(status_code_actual_value, status_code_accepted_value)


if __name__ == '__main__':
    unittest.main()
