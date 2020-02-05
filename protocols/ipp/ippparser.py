from protocols.ipp.common import load_enum
from protocols.ipp.common import load_json_file

from pathlib import Path

string_tags = [num for num in range(64, 96)]
out_of_band_tags = [16, 18, 19]
enum_tag = 35
boolean_tag = 34
integer_tag = 33
date_time_tag = 49
resolution_tag = 50
range_of_integer_tag = 51
collection = 52
octet_string_tag = 48


def calculate_length(len_list):
    """
    function to calculate length
    """
    length = int("".join(len_list), 16)
    return length


def get_delimiter_field_name(field):
    """
    function to return delimiter field name
    """
    delimiter_name = ""
    ipp_attr_group_tags = load_json_file(str(Path("protocols/ipp/ipp_data/ipp_attribute_group_tags.json")))
    for key, value in ipp_attr_group_tags.items():
        if int(field) == value:
            delimiter_name = key
            break

    return delimiter_name


def get_value_tag_field_name(field):
    """
    function to return value tag field name
    """
    value_tag_name = ""
    ipp_value_tags = load_json_file(str(Path("protocols/ipp/ipp_data/ipp_attributes_value_tags.json")))
    for key, value in ipp_value_tags.items():
        if int(field, 16) == value:
            value_tag_name = key
            break

    return value_tag_name


def get_enum_tag_field_name(name, value):
    _enum_tag = load_enum()

    if name in _enum_tag.keys():
        for key, val in _enum_tag[name].items():
            if str(value) == str(val):
                return key

    return "No Enum value is present"


def get_date_time(value):
    year = int("".join(value[:2]), 16)
    month = int("".join(value[2]), 16)
    day = int("".join(value[3]), 16)
    hour = int("".join(value[4]), 16)
    _min = int("".join(value[5]), 16)
    sec = int("".join(value[6]), 16)
    deci_sec = int("".join(value[7]), 16)
    utc = bytes.fromhex("".join(value[8])).decode()
    hrs_from_utc = int("".join(value[9]), 16)
    mins_from_utc = int("".join(value[10]), 16)

    return f"{str(year)}-{str(month)}-{str(day)} {str(hour)}:{str(_min)}:{str(sec)}.{str(deci_sec)} {str(utc)}" \
           f"{str(hrs_from_utc)}{str(mins_from_utc)}"


def get_resolution(value):
    x_res = int("".join(value[:4]), 16)
    y_res = int("".join(value[4:8]), 16)
    dpi = "dpi" if int("".join(value[-1]), 16) == 3 else "Unknown Unit"

    return f"{str(x_res)}X{str(y_res)} {dpi}"


def get_range_of_integer(value):
    first_four_bytes = int("".join(value[:4]), 16)
    second_four_bytes = int("".join(value[4:]), 16)
    return f"{str(first_four_bytes)}-{str(second_four_bytes)}"


def get_attribute_name(hex_list):
    length = calculate_length(hex_list[:2])

    if length > 0:
        attribute_name = bytes.fromhex("".join(hex_list[2:length + 2])).decode()
        _hex_list = hex_list[length + 2:]
    else:
        attribute_name = ""
        _hex_list = hex_list[2:]

    return attribute_name, _hex_list


def get_attribute_value(hex_list):
    return get_attribute_name(hex_list)


def get_string_tags(hex_list, value_tag_hex):
    value_tag = [value_tag_hex, '00', '00']
    value_tag_name = get_value_tag_field_name(value_tag_hex)
    data = dict()

    attribute_name, hex_list = get_attribute_name(hex_list)

    attribute_value, hex_list = get_attribute_value(hex_list)

    attribute_values = [attribute_value]

    while hex_list[:3] == value_tag:
        length = calculate_length(hex_list[3:5])
        attribute_value = bytes.fromhex("".join(hex_list[5:length + 5])).decode()
        attribute_values.append(attribute_value)
        hex_list = hex_list[length + 5:]

    if len(attribute_values) > 1:
        data[f"{attribute_name}(1setOf {value_tag_name})"] = attribute_values
    else:
        data[f"{attribute_name}({value_tag_name})"] = attribute_values

    return data, hex_list


def get_out_of_band_tags(hex_list, value_tag_hex):
    return get_string_tags(hex_list, value_tag_hex)


def get_enum_tags(hex_list, value_tag_hex):
    value_tag = [value_tag_hex, '00', '00']
    value_tag_name = get_value_tag_field_name(value_tag_hex)
    data = dict()

    attribute_name, hex_list = get_attribute_name(hex_list)

    length = calculate_length(hex_list[:2])
    attribute_values = [get_enum_tag_field_name(attribute_name, int("".join(hex_list[2:length + 2]), 16))]
    hex_list = hex_list[length + 2:]

    while hex_list[:3] == value_tag:
        length = calculate_length(hex_list[3:5])
        attribute_value = get_enum_tag_field_name(attribute_name, int("".join(hex_list[5:length + 5]), 16))
        attribute_values.append(attribute_value)
        hex_list = hex_list[length + 5:]

    if len(attribute_values) > 1:
        data[f"{attribute_name}(1setOf {value_tag_name})"] = attribute_values
    else:
        data[f"{attribute_name}({value_tag_name})"] = attribute_values

    return data, hex_list


def get_boolean_tags(hex_list, value_tag_hex):
    value_tag = [value_tag_hex, '00', '00']
    value_tag_name = get_value_tag_field_name(value_tag_hex)
    data = dict()

    attribute_name, hex_list = get_attribute_name(hex_list)

    length = calculate_length(hex_list[:2])
    raw_value = int("".join(hex_list[2:length + 2]), 16)

    attribute_values = ['True' if raw_value == 1 else 'False']
    hex_list = hex_list[length + 2:]

    while hex_list[:3] == value_tag:
        length = calculate_length(hex_list[3:5])
        raw_value = int("".join(hex_list[5:length + 5]), 16)
        attribute_value = 'True' if raw_value == 1 else 'False'
        attribute_values.append(attribute_value)
        hex_list = hex_list[length + 5:]

    if len(attribute_values) > 1:
        data[f"{attribute_name}(1setOf {value_tag_name})"] = attribute_values
    else:
        data[f"{attribute_name}({value_tag_name})"] = attribute_values

    return data, hex_list


def get_integer_tags(hex_list, value_tag_hex):
    value_tag = [value_tag_hex, '00', '00']
    value_tag_name = get_value_tag_field_name(value_tag_hex)
    data = dict()

    attribute_name, hex_list = get_attribute_name(hex_list)

    length = calculate_length(hex_list[:2])
    attribute_values = [int("".join(hex_list[2:length + 2]), 16)]
    hex_list = hex_list[length + 2:]

    while hex_list[:3] == value_tag:
        length = calculate_length(hex_list[3:5])
        attribute_value = int("".join(hex_list[5:length + 5]), 16)
        attribute_values.append(attribute_value)
        hex_list = hex_list[length + 5:]

    if len(attribute_values) > 1:
        data[f"{attribute_name}(1setOf {value_tag_name})"] = attribute_values
    else:
        data[f"{attribute_name}({value_tag_name})"] = attribute_values

    return data, hex_list


def get_datetime_tags(hex_list, value_tag_hex):
    value_tag = [value_tag_hex, '00', '00']
    value_tag_name = get_value_tag_field_name(value_tag_hex)
    data = dict()

    attribute_name, hex_list = get_attribute_name(hex_list)

    length = calculate_length(hex_list[:2])
    attribute_values = [get_date_time(hex_list[2:length + 2])]
    hex_list = hex_list[length + 2:]

    while hex_list[:3] == value_tag:
        length = calculate_length(hex_list[3:5])
        attribute_value = get_date_time(hex_list[5:length + 5])
        attribute_values.append(attribute_value)
        hex_list = hex_list[length + 5:]

    if len(attribute_values) > 1:
        data[f"{attribute_name}(1setOf {value_tag_name})"] = attribute_values
    else:
        data[f"{attribute_name}({value_tag_name})"] = attribute_values

    return data, hex_list


def get_resolution_tags(hex_list, value_tag_hex):
    value_tag = [value_tag_hex, '00', '00']
    value_tag_name = get_value_tag_field_name(value_tag_hex)
    data = dict()

    attribute_name, hex_list = get_attribute_name(hex_list)

    length = calculate_length(hex_list[:2])
    attribute_values = [get_resolution(hex_list[2:length + 2])]
    hex_list = hex_list[length + 2:]

    while hex_list[:3] == value_tag:
        length = calculate_length(hex_list[3:5])
        attribute_value = get_resolution(hex_list[5:length + 5])
        attribute_values.append(attribute_value)
        hex_list = hex_list[length + 5:]

    if len(attribute_values) > 1:
        data[f"{attribute_name}(1setOf {value_tag_name})"] = attribute_values
    else:
        data[f"{attribute_name}({value_tag_name})"] = attribute_values

    return data, hex_list


def get_range_of_integer_tag(hex_list, value_tag_hex):
    value_tag = [value_tag_hex, '00', '00']
    value_tag_name = get_value_tag_field_name(value_tag_hex)
    data = dict()

    attribute_name, hex_list = get_attribute_name(hex_list)

    length = calculate_length(hex_list[:2])
    attribute_values = [get_range_of_integer(hex_list[2:length + 2])]
    hex_list = hex_list[length + 2:]

    while hex_list[:3] == value_tag:
        length = calculate_length(hex_list[3:5])
        attribute_value = get_range_of_integer(hex_list[5:length + 5])
        attribute_values.append(attribute_value)
        hex_list = hex_list[length + 5:]

    if len(attribute_values) > 1:
        data[f"{attribute_name}(1setOf {value_tag_name})"] = attribute_values
    else:
        data[f"{attribute_name}({value_tag_name})"] = attribute_values

    return data, hex_list


def get_octet_string_tag(hex_list, value_tag_hex):
    value_tag = [value_tag_hex, '00', '00']
    value_tag_name = get_value_tag_field_name(value_tag_hex)
    data = dict()

    attribute_name, hex_list = get_attribute_name(hex_list)

    length = calculate_length(hex_list[:2])
    attribute_values = [bytes.fromhex("".join(hex_list[2:length + 2])).decode()]
    hex_list = hex_list[length + 2:]

    while hex_list[:3] == value_tag:
        length = calculate_length(hex_list[3:5])
        attribute_value = bytes.fromhex("".join(hex_list[5:length + 5])).decode()
        attribute_values.append(attribute_value)
        hex_list = hex_list[length + 5:]

    if len(attribute_values) > 1:
        data[f"{attribute_name}(1setOf {value_tag_name})"] = attribute_values
    else:
        data[f"{attribute_name}({value_tag_name})"] = attribute_values

    return data, hex_list


def get_collection_tag(hex_list, value_tag_hex):

    _data = dict()
    end_collection = False

    # get name value
    beg_collection, hex_list = get_attribute_name(hex_list)
    hex_list = hex_list[2:]
    nested_tag = ""

    _tmp_dict = dict()

    while not end_collection:

        if int(hex_list[0], 16) == 74:
            value, hex_list = get_attribute_value(hex_list[3:])

            if int(hex_list[0], 16) == collection:
                # check if nested collection starts
                nested_tag = value
                _tmp_dict[value] = dict()
                hex_list = hex_list[5:]

            elif int(hex_list[0], 16) == integer_tag:
                # parse integer values
                value_tag_name = get_value_tag_field_name(hex_list[0])
                ipp_hex_list = hex_list[3:]
                length = calculate_length(ipp_hex_list[:2])
                attribute_value = int("".join(ipp_hex_list[2:length + 2]), 16)
                hex_list = ipp_hex_list[length + 2:]

                if nested_tag != "":
                    _tmp_dict[nested_tag].update({value: f"{attribute_value}({value_tag_name})"})
                else:
                    _tmp_dict.update({value: f"{attribute_value}({value_tag_name})"})

            elif int(hex_list[0], 16) in string_tags:
                # parse string values
                value_tag_name = get_value_tag_field_name(hex_list[0])
                ipp_hex_list = hex_list[3:]
                length = calculate_length(ipp_hex_list[:2])
                attribute_value = bytes.fromhex("".join(ipp_hex_list[2:length + 2])).decode()
                hex_list = ipp_hex_list[length + 2:]

                if nested_tag != "":
                    _tmp_dict[nested_tag].update({value: f"{attribute_value}({value_tag_name})"})
                else:
                    _tmp_dict.update({value: f"{attribute_value}({value_tag_name})"})

            elif int(hex_list[0], 16) in out_of_band_tags:
                value_tag_name = get_value_tag_field_name(hex_list[0])
                ipp_hex_list = hex_list[3:]
                length = calculate_length(ipp_hex_list[:2])
                attribute_value = bytes.fromhex("".join(ipp_hex_list[2:length + 2])).decode()
                hex_list = ipp_hex_list[length + 2:]

                if nested_tag != "":
                    _tmp_dict[nested_tag].update({value: f"{attribute_value}({value_tag_name})"})
                else:
                    _tmp_dict.update({value: f"{attribute_value}({value_tag_name})"})

            elif int(hex_list[0], 16) == enum_tag:
                # parse enum values
                value_tag_name = get_value_tag_field_name(hex_list[0])
                ipp_hex_list = hex_list[3:]
                length = calculate_length(ipp_hex_list[:2])
                attribute_value = get_enum_tag_field_name(value, int("".join(ipp_hex_list[2:length + 2]), 16))
                hex_list = ipp_hex_list[length + 2:]

                if nested_tag != "":
                    _tmp_dict[nested_tag].update({value: f"{attribute_value}({value_tag_name})"})
                else:
                    _tmp_dict.update({value: f"{attribute_value}({value_tag_name})"})

            elif int(hex_list[0], 16) == boolean_tag:
                # parse boolean values
                value_tag_name = get_value_tag_field_name(hex_list[0])
                ipp_hex_list = hex_list[3:]
                length = calculate_length(ipp_hex_list[:2])
                raw_value = int("".join(ipp_hex_list[2:length + 2]), 16)
                attribute_value = "True" if raw_value == 1 else "False"
                hex_list = ipp_hex_list[length + 2:]

                if nested_tag != "":
                    _tmp_dict[nested_tag].update({value: f"{attribute_value}({value_tag_name})"})
                else:
                    _tmp_dict.update({value: f"{attribute_value}({value_tag_name})"})

            elif int(hex_list[0], 16) == date_time_tag:
                # parse dateTime
                value_tag_name = get_value_tag_field_name(hex_list[0])
                ipp_hex_list = hex_list[3:]
                length = calculate_length(ipp_hex_list[:2])
                attribute_value = get_date_time(ipp_hex_list[2:length+2])
                hex_list = ipp_hex_list[length + 2:]

                if nested_tag != "":
                    _tmp_dict[nested_tag].update({value: f"{attribute_value}({value_tag_name})"})
                else:
                    _tmp_dict.update({value: f"{attribute_value}({value_tag_name})"})

            elif int(hex_list[0], 16) == resolution_tag:
                # parse resolution
                value_tag_name = get_value_tag_field_name(hex_list[0])
                ipp_hex_list = hex_list[3:]
                length = calculate_length(ipp_hex_list[:2])
                attribute_value = get_resolution(ipp_hex_list[2:length + 2])
                hex_list = ipp_hex_list[length + 2:]

                if nested_tag != "":
                    _tmp_dict[nested_tag].update({value: f"{attribute_value}({value_tag_name})"})
                else:
                    _tmp_dict.update({value: f"{attribute_value}({value_tag_name})"})

            elif int(hex_list[0], 16) == range_of_integer_tag:
                # parse range of integer
                value_tag_name = get_value_tag_field_name(hex_list[0])
                ipp_hex_list = hex_list[3:]
                length = calculate_length(ipp_hex_list[:2])
                attribute_value = get_range_of_integer(ipp_hex_list[2:length + 2])
                hex_list = ipp_hex_list[length + 2:]

                if nested_tag != "":
                    _tmp_dict[nested_tag].update({value: f"{attribute_value}({value_tag_name})"})
                else:
                    _tmp_dict.update({value: f"{attribute_value}({value_tag_name})"})

            elif int(hex_list[0], 16) == octet_string_tag:
                # parse octet string
                value_tag_name = get_value_tag_field_name(hex_list[0])
                ipp_hex_list = hex_list[3:]
                length = calculate_length(ipp_hex_list[:2])
                attribute_value = bytes.fromhex("".join(ipp_hex_list[2:length + 2])).decode()
                hex_list = ipp_hex_list[length + 2:]

                if nested_tag != "":
                    _tmp_dict[nested_tag].update({value: f"{attribute_value}({value_tag_name})"})
                else:
                    _tmp_dict.update({value: f"{attribute_value}({value_tag_name})"})

        elif int(hex_list[0], 16) == 55:
            # check if nested collection ends
            nested_tag = ""
            hex_list = hex_list[5:]

        else:
            end_collection = True

    _data[beg_collection] = _tmp_dict

    return _data, hex_list