from scapy.packet import Packet
from pathlib import Path

from protocols.ipp.ipp_logger import get_logger
from protocols.ipp.common import load_json_file
from protocols.ipp.ippparser import get_delimiter_field_name, get_string_tags, get_out_of_band_tags, \
    get_enum_tags, get_boolean_tags, get_integer_tags, get_datetime_tags, get_resolution_tags,\
    get_range_of_integer_tag, get_collection_tag, get_octet_string_tag

# delimiter_tags_fields_value
delimiter_tag = [num for num in range(0, 16)]
string_tags = [num for num in range(64, 96)]
out_of_band_tags = [16, 18, 19]
enum_tag = 35
boolean_tag = 34
integer_tag = 33
date_time_tag = 49
resolution_tag = 50
range_of_integer_tag = 51
collection_tag = 52
octet_string_tag = 48

logger = get_logger("IPP Parsing")


def _parse_headers(s):
    logger.info("Parsing Headers")
    headers = s.split(b"\r\n")
    headers_found = {}
    for header_line in headers:
        try:
            key, value = header_line.split(b':', 1)
        except ValueError:
            continue
        headers_found[key.decode()] = value.strip().decode()
    logger.info("Header Parsing Done")
    return headers_found


def _parse_body(body):
    logger.info("Parsing Body")
    crlf = b"\r\n"
    new_body = b""
    while body:
        if body == b'0\r\n\r\n':
            body = b""
        else:
            crlfindex = body.find(crlf)
            chunk = int(body[:crlfindex].decode(), 16)
            new_body = new_body + body[len(crlf)+crlfindex: chunk+len(crlf)+crlfindex]
            body = body[chunk+len(crlf)*2+crlfindex:]
    logger.info("Parsing Body Done")
    return new_body


def _parse_headers_and_body(val):
    logger.info("Looking for header and body")
    crlfcrlf = b"\r\n\r\n"
    crlfcrlfindex = val.find(crlfcrlf)
    if crlfcrlfindex != -1:
        headers = val[:crlfcrlfindex + len(crlfcrlf)]
        body = val[crlfcrlfindex + len(crlfcrlf):]
    else:
        headers = val
        body = b''

    first_line, headers = headers.split(b"\r\n", 1)
    return first_line.strip(), _parse_headers(headers), body


def _dissect_values(val):
    first_line, headers, body = _parse_headers_and_body(val)

    return first_line, headers, _parse_body(body)


def _ipp_parser(val):
    logger.info("Parsing IPP Values from body")
    from scapy.utils import chexdump
    values = {}

    a = chexdump(val, True)
    a = a.replace(" ", "").split(",")
    new_val = [i[2:] for i in a]

    # version
    ver = new_val[:2]
    ver_decimal = ".".join([str(int(v, 16)) for v in ver])
    values['version'] = ver_decimal

    # status code
    status_code = "".join(new_val[2:4])
    status_code_decimal = int(status_code, 16)

    ipp_status_codes = load_json_file(str(Path("protocols/ipp/ipp_data/ipp_status_codes.json")))

    for key, value in ipp_status_codes.items():
        if status_code_decimal == value:
            values['status-code'] = key
            break

        else:
            values['status-code'] = 'server-error'

    # request-id
    request_id = "".join(new_val[4:8])
    request_id_decimal = int(request_id, 16)
    values['request-id'] = request_id_decimal

    # remaining values
    delimiter_name = ""
    ipp_dict = dict()

    ipp_hex_list = new_val[8:]

    count = 0
    while ipp_hex_list:

        first_byte = ipp_hex_list[0]

        # check if delimiter field is present in 1st place
        if int(first_byte, 16) in delimiter_tag:
            delimiter_name = get_delimiter_field_name(first_byte)

            if delimiter_name in ipp_dict.keys():
                count += 1
                delimiter_name = f"{delimiter_name}-{str(count)}"

            ipp_dict[delimiter_name] = dict()

            # remove first byte from ipp_hex_list
            ipp_hex_list = ipp_hex_list[1:]
            continue

        if int(first_byte, 16) in string_tags:
            ipp_hex_list = ipp_hex_list[1:]
            value_tag_hex = first_byte
            data, ipp_hex_list = get_string_tags(ipp_hex_list, value_tag_hex)
            ipp_dict[delimiter_name].update(data)

        elif int(first_byte, 16) in out_of_band_tags:
            ipp_hex_list = ipp_hex_list[1:]
            value_tag_hex = first_byte
            data, ipp_hex_list = get_out_of_band_tags(ipp_hex_list, value_tag_hex)
            ipp_dict[delimiter_name].update(data)

        elif int(first_byte, 16) == enum_tag:
            # parse enum values
            ipp_hex_list = ipp_hex_list[1:]
            value_tag_hex = first_byte
            data, ipp_hex_list = get_enum_tags(ipp_hex_list, value_tag_hex)
            ipp_dict[delimiter_name].update(data)

        elif int(first_byte, 16) == boolean_tag:
            # parse boolean values
            ipp_hex_list = ipp_hex_list[1:]
            value_tag_hex = first_byte
            data, ipp_hex_list = get_boolean_tags(ipp_hex_list, value_tag_hex)
            ipp_dict[delimiter_name].update(data)

        elif int(first_byte, 16) == integer_tag:
            # parse integer values
            ipp_hex_list = ipp_hex_list[1:]
            value_tag_hex = first_byte
            data, ipp_hex_list = get_integer_tags(ipp_hex_list, value_tag_hex)
            ipp_dict[delimiter_name].update(data)

        elif int(first_byte, 16) == date_time_tag:
            # parse dateTime
            ipp_hex_list = ipp_hex_list[1:]
            value_tag_hex = first_byte
            data, ipp_hex_list = get_datetime_tags(ipp_hex_list, value_tag_hex)
            ipp_dict[delimiter_name].update(data)

        elif int(first_byte, 16) == resolution_tag:
            # parse resolution
            ipp_hex_list = ipp_hex_list[1:]
            value_tag_hex = first_byte
            data, ipp_hex_list = get_resolution_tags(ipp_hex_list, value_tag_hex)
            ipp_dict[delimiter_name].update(data)

        elif int(first_byte, 16) == range_of_integer_tag:
            # parse range of integer
            ipp_hex_list = ipp_hex_list[1:]
            value_tag_hex = first_byte
            data, ipp_hex_list = get_range_of_integer_tag(ipp_hex_list, value_tag_hex)
            ipp_dict[delimiter_name].update(data)

        elif int(first_byte, 16) == collection_tag:
            # parse collection tag
            ipp_hex_list = ipp_hex_list[1:]
            value_tag_hex = first_byte
            data, ipp_hex_list = get_collection_tag(ipp_hex_list, value_tag_hex)
            ipp_dict[delimiter_name].update(data)

        elif int(first_byte, 16) == octet_string_tag:
            # parse octet string
            ipp_hex_list = ipp_hex_list[1:]
            value_tag_hex = first_byte
            data, ipp_hex_list = get_octet_string_tag(ipp_hex_list, value_tag_hex)
            ipp_dict[delimiter_name].update(data)

    values.update(ipp_dict)
    logger.info("Parsing IPP Values from body Completed")

    return values


class IPP(Packet):
    name = "IPP"
    fields_desc = []
    bind_values = b""
    logger = get_logger(f"IPP Packet Forming")

    @classmethod
    def add_fields(cls, values):
        IPP.logger.info("Adding IPP Packets")
        for val in values:
            cls.fields_desc.append(val)

        IPP.logger.info("Adding IPP Packets Completed")

    def do_dissect(self, s):
        IPP.logger.info("Dissecting IPP Packets")
        IPP.bind_values = IPP.bind_values + s
        IPP.logger.info("IPP Dissecting Completed")

    @classmethod
    def get_results(cls):
        IPP.logger.info("Getting Results")
        first_line, headers, body = _dissect_values(IPP.bind_values)

        first_line = first_line.decode()
        headers = headers
        body = _ipp_parser(body)
        IPP.logger.info("Returning Results")
        return first_line, headers, body



