def get_jobs(printer_uri):
    """
    Basic IPP Get Jobs Template
    """
    from getpass import getuser
    uri = f"ipp://{printer_uri}/ipp/print"

    operation_attributes_tag = {
        "attributes-charset": "utf-8",
        "attributes-natural-language": "en-us",
        "printer-uri": f"{uri}",
        "requesting-user-name": f"{getuser()}",
        "which-jobs": "completed"
    }

    _get_jobs = {
        "operation-attributes-tag": operation_attributes_tag,
    }

    return _get_jobs
