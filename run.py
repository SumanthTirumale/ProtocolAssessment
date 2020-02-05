from protocols.ipp.wrapper import IPP
from protocols.ipp.common import get_raw_data


def print_job():
    operation_attributes_tag = {
        "attributes-charset": "utf-8",
        "attributes-natural-language": "en-us",
        "printer-uri": "ipp://192.168.80.78/ipp/print",
        "requesting-user-name": "SVA-Automation",
        "job-name": "TABLES.pdf",
    }

    job_attributes_tag = {}

    data = get_raw_data("TABLES.pdf")

    _print_job = {
        "operation-attributes-tag": operation_attributes_tag,
        "job-attributes-tag": job_attributes_tag,
        "data": data
    }

    return _print_job


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


def get_jobs():
    operation_attributes_tag = {
        "attributes-charset": "utf-8",
        "attributes-natural-language": "en-us",
        "printer-uri": "ipp://192.168.80.189/ipp/print",
        "requesting-user-name": "SVA-Automation",
        "which-jobs": "completed,new"
    }

    _get_jobs = {
        "operation-attributes-tag": operation_attributes_tag,
    }

    return _get_jobs


if __name__ == "__main__":

    ipp = IPP("192.168.80.78")

    first_line, headers, body = ipp.send(op_type="Get-Printer-Attributes", version=1.1, **get_printer_attributes())

    print(first_line)
    print(headers)
    print(body)


