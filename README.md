# Protocol Assessment
Protocol Assessment is a packet manipulation framework. Developed using Python and Scapy.
It is used to form and send protocol packets.

## Installation

* Download the package from [dist](https://github.com/SumanthTirumale/ProtocolAssessment/tree/master/dist) directory  
* Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Protocol Assessment 

```bash
pip install ProtocolAssessment-1.X.X-py3-none-any.whl
```

## Usage
* With Unittest framework 
```python
import unittest
from protocols.ipp.wrapper import IPP


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.host = "192.X.X.X"
        self.ipp = IPP(self.host)

    @staticmethod
    def get_printer_attributes():
        operation_attributes_tag = {
            "attributes-charset": "utf-8",
            "attributes-natural-language": "en-us",
            "printer-uri": "ipp://192.X.X.X/ipp/print",
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
```
* Without Unittest framework

```python
from protocols.ipp.wrapper import IPP


def get_printer_attributes():
    operation_attributes_tag = {
        "attributes-charset": "utf-8",
        "attributes-natural-language": "en-us",
        "printer-uri": "ipp://192.X.X.X/ipp/print",
    }

    _get_printer_attributes = {
        "operation-attributes-tag": operation_attributes_tag,
    }

    return _get_printer_attributes

if __name__ == "__main__":

    ipp = IPP("192.X.X.X")

    first_line, headers, body = ipp.send(op_type="Get-Printer-Attributes", version=1.1, **get_printer_attributes())

    print(first_line)
    print(headers)
    print(body)
```

## License
[MIT](https://choosealicense.com/licenses/mit/)