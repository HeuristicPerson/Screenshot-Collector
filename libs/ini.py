# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------------------------------------------------
# Library for parsing ini files
#-----------------------------------------------------------------------------------------------------------------------

import os
import sys
#import pf_logger


class ParsedIni:
    """
    Class to contain parsed data from ini files and a method to read a particular value.
    """

    def __init__(self, s_file):
        if os.path.isfile(s_file):
            #TODO: write a couple of checks to accidentaly open a non-ini file or excesive big ini files.
            o_file = open(s_file, 'r')
            self.__dds_data = _parse(o_file)
            o_file.close()

        else:
            sys.exit()

    def __iter__(self):
        for s_key, ds_values in self.__dds_data.items():
            yield {'section': s_key, 'values': ds_values}

    def get(self, s_section, s_field):
        """
        Method for reading the value of a field inside a section.

        :param s_section: Name of the section, identified by square brackets. i.e. For '[menu]', s_section = 'menu'.
            NOTE: s_section is NOT case sensitive. i.e. 'main' and 'Main' are the same section.

        :param s_field: Name of the field, just before =. i.e. For 'stars = 10', s_field = 'stars'. NOTE: s_field is NOT
            case sensitive. i.e. 'Start' and 'start' are the same field.

        :return s_output: Value after =. i.e. For 'stars = 10', s_output = '10' NOTICE IT'S ALWAYS A STRING!
        """

        if (s_section in self.__dds_data) and (s_field in self.__dds_data[s_section]):
            s_output = self.__dds_data[s_section][s_field]
        else:
            s_output = ''

        return s_output

    def set(self, s_section, s_field, value):
        """Method for setting a new field/value couple inside a section"""

        self.__dds_data[s_section][s_field] = str(value)

        #pf_logger.log('Set to ini: [%s] %s = %s' % (s_section, s_field, str(value)))


def list_float(s_string):
    # todo: to delete
    """
    Function that converts and clean a string with ',' to a tuple of floats.

    s_string:
        The string. i.e. '1.5, 3, 6.5, 7, 23.01'
    """

    lf_output = []
    ls_strings = s_string.split(',')

    for s_element in ls_strings:
        s_element = s_element.strip()
        f_element = float(s_element)
        lf_output.append(f_element)

    return lf_output


def tuple_int(s_string):
    # todo: to delete
    """Function that converts and clean a string with ',' to a tuple of integers.

    s_string:
        The string. i.e. '1, 3, 6, 7, 23'
    """

    ti_output = ()
    ls_strings = s_string.split(',')

    for s_element in ls_strings:
        s_element = s_element.strip()
        i_element = int(s_element)
        ti_output += (i_element, )

    return ti_output


def list_str(s_string):
    # todo: to delete
    """Function that converts and clean a string with ',' to a tuple of integers.

    s_string:
        The string. i.e. 'abc, efg, tuv'
    """

    ls_output = []
    ls_strings = s_string.split(',')

    for s_element in ls_strings:
        s_element = s_element.strip()
        ls_output.append(s_element)

    return ls_output


def write(o_file, s_sec, s_id, s_mode='string'):
    """
    Function for reading data from a structured ini o_file

    o_file:
        file object where the information is gathered from.

    s_sec:
        section where the data is. i.e. "[Main]" -> s_sec = 'Main'

    __s_id:
        identifier of the data. i.e. "width = 200" -> __s_id = 'width'

    s_mode:
        type of data that's going to be read.o_file. Valid values: 'integer', 'float', 'string'
    """

    # TODO: create the function to write fields and data in an ini file.
    # it will be useful in the future for direct creation of ini files from the program itself or from a different gui


def _parse(o_file):
    """
    Function to parse an ini file and returns a structured dictionary of dictionaries. All the data generated will
    be dictionary(key=string:data=dictionary(key=string:data=string). So, after using this function, you should convert
    the strings to integers or floats in case you needed it.

    o_file:
        file object where the information is gathered from.o_file

    input data example:
    [Main]
    a = 14
    b = 56
    [Screen]
    w = 640

    output data:
    {'Main':{'a':'14', 'b':'56'}, 'Screen':{'v':'640'}}
    """

    s_section = ''
    dds_data = {}
    ds_pair = {}

    for s_line in o_file:
        # again, I should figure a way to avoid explicit encoding format
        s_line = s_line.decode('utf8')
        # cleaning out comments in the ini
        s_line = s_line.partition(';')[0]

        # todo: improve code because a [ or ] after = could trigger the section and that's a BIG ERROR

        i_start = s_line.find('[')
        i_end = s_line.find(']', i_start)

        if i_start != -1 and i_end != -1:
            s_section = s_line[i_start + 1:i_end]
            s_section = s_section.lower()
            ds_pair = {}
        else:
            if s_line.find('=') != -1:
                s_left = s_line.partition('=')[0]
                s_left = s_left.strip()
                s_left = s_left.lower()

                s_right = s_line.partition('=')[2]
                s_right = s_right.strip()

                if s_left != '':
                    ds_pair[s_left] = s_right
                    dds_data[s_section] = ds_pair

    return dds_data
