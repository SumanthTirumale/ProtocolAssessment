from protocols.ipp.ipp import IPP as InternetPrintingProtocol
from protocols.ipp.common import load_json_file, load_enum_data
from protocols.ipp.ipp_logger import get_logger
from protocols.ipp.ipp_templates import *
from scapy.all import StreamSocket
from scapy.layers.http import HTTP, HTTPRequest
from scapy.fields import ShortField, XByteField, StrField, SignedShortField, SignedIntField
from pathlib import Path

import socket

import sys

IPP_HTTP_REQUESTS = {
    "Method": b'POST',
    "Connection": b'Keep-Alive',
    "Content_Type": b'application/ipp',
    "User_Agent": b'Internet Print Provider',
}


class IPP:

    def __init__(self, host, port=631, path="/ipp/print"):
        self.host = host
        self.port = int(port)
        self.path = "/" + path if path[0] != "/" else path

        self.my_socket = None
        self.my_stream = None

        # main ipp data field
        self.ipp_field = list()

        # all ipp attributes
        self.ipp_attr_group_tags = dict()
        self.ipp_attrs = dict()
        self.ipp_enums = dict()
        self.ipp_operations = dict()
        self.ipp_value_tags = dict()

        self.load_ipp_data()
        self.connect()

    def load_ipp_data(self):
        """
        Method to load all ipp data
        """
        logger = get_logger("Load ipp Data")
        logger.info("loading ipp required data")

        self.ipp_attr_group_tags = load_json_file(
            str(Path("protocols/ipp/ipp_data/ipp_attribute_group_tags.json"))
        )

        self.ipp_attrs = load_json_file(
            str(Path("protocols/ipp/ipp_data/ipp_attributes.json"))
        )

        self.ipp_operations = load_json_file(
            str(Path("protocols/ipp/ipp_data/ipp_operations.json"))
        )

        self.ipp_value_tags = load_json_file(
            str(Path("protocols/ipp/ipp_data/ipp_attributes_value_tags.json"))
        )

        self.ipp_enums = load_enum_data(
            str(Path("protocols/ipp/ipp_data/ipp_enum.json"))
        )

        logger.info("loading ipp required data completed")

    def connect(self):
        """
        Method to initiate 3 way handshake
        """
        logger = get_logger("Three Way Handshake")
        logger.info("Initiating Three way Handshake")
        try:

            self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.my_socket.connect((self.host, self.port))
            self.my_stream = StreamSocket(self.my_socket)
            self.my_stream.basecls = InternetPrintingProtocol

        except socket.error as exc:
            logger.critical(f"Socket Error {exc}")

        finally:
            logger.info("Three way handshake completed")

    def form_ipp_packet(self, op_type, version=1.0, **kwargs):
        """
        Method to form ipp packets
        """

        logger = get_logger("IPP Packet Forming")
        logger.info("Initiating IPP Packet Crafting")

        ver = str(version).split(".")
        ver = "".join(ver)
        ver = SignedShortField("Version", int(ver))

        self.ipp_field.append(ver)

        data = ""

        operation_type = op_type

        if operation_type in self.ipp_operations.keys():

            self.ipp_field.append(SignedShortField("Operation-ID", self.ipp_operations[operation_type]))
            self.ipp_field.append(SignedIntField("Request-ID", self.ipp_operations[operation_type]))
        else:
            logger.critical(f"Invalid operation tag : {operation_type}")
            print('Supported Operations')
            for op_rst in list(self.ipp_operations.keys()):
                print(f"* {op_rst}")
            sys.exit()

        delete_key = list()

        for delimiter_key, delimiter_value in kwargs.items():
            if type(delimiter_value) != dict:
                data = delimiter_value
                delete_key.append(delimiter_key)

        if len(delete_key) > 0:
            for del_key in delete_key:
                del kwargs[del_key]

        for delimiter_key, delimiter_value in kwargs.items():

            if type(delimiter_value) == dict:

                if delimiter_key in self.ipp_attr_group_tags.keys():

                    self.ipp_field.append(XByteField(delimiter_key, self.ipp_attr_group_tags[delimiter_key]))

                    count = 0
                    for attr_key, attr_val in delimiter_value.items():

                        if attr_key in self.ipp_attrs.keys():

                            self.ipp_field.append(XByteField(f"key_{attr_key}_{count}", self.ipp_attrs[attr_key][1]))

                            self.ipp_field.append(ShortField(f"Attribute_Name_Length_{count}", len(attr_key)))
                            self.ipp_field.append(
                                StrField(f"Attribute_Name_Value_{attr_key}_{count}", bytes(attr_key, encoding='utf8'))
                            )

                            self.ipp_field.append(ShortField(f"Attribute_Value_Length_{count}", len(attr_val)))
                            self.ipp_field.append(
                                StrField(f"Attribute_Value_Value_{attr_val}_{count}", bytes(attr_val, encoding='utf8'))
                            )

                            count += 1

                        else:
                            logger.critical(f"Invalid Attribute tag : {attr_key}")
                            sys.exit()
                else:
                    logger.critical(f"Invalid Delimiter tag : {delimiter_key}")
                    print("Supported Tags")
                    for del_tag in list(self.ipp_attr_group_tags.keys()):
                        print(f"* {del_tag}")
                    sys.exit()

            else:
                logger.critical(f"Invalid tag : {delimiter_key}")
                sys.exit()

        self.ipp_field.append(XByteField("end-of-attributes-tag", self.ipp_attr_group_tags["end-of-attributes-tag"]))
        if data != "":
            self.ipp_field.append(StrField("Data", data))
        logger.info("IPP Packet forming completed")

    def send(self, op_type, version, **kwargs):
        """
        Method to send and receive ipp request
        """

        if len(kwargs) <= 0:

            if op_type == "Get-Jobs":
                kwargs = get_jobs(self.host)
            else:
                print(f"No default templates is available for {op_type} !!!")
                sys.exit()

        self.form_ipp_packet(op_type=op_type, version=version, **kwargs)

        InternetPrintingProtocol.add_fields(self.ipp_field)

        IPP_HTTP_REQUESTS['Content_Length'] = bytes(str(len(InternetPrintingProtocol())), "utf-8")
        IPP_HTTP_REQUESTS['Host'] = bytes(f"{self.host}:{self.port}", "utf-8")
        IPP_HTTP_REQUESTS['Path'] = bytes(self.path, "utf-8")

        ipp_request = HTTP()/HTTPRequest(**IPP_HTTP_REQUESTS)/InternetPrintingProtocol()

        self.my_stream.sr(ipp_request, timeout=5, verbose=0)

        return InternetPrintingProtocol().get_results()