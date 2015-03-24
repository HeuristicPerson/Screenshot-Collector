# -*- coding: utf-8 -*-


#=======================================================================================================================
# Library for parsing ini files
#=======================================================================================================================

import os
import sys


class ParsedIni:
    """
    Class to contain parsed data from ini files and a method to read a particular value.
    """

    def __init__(self):
        # Values definition
        self._do_sections = dict()

        # Variables to use in the iteration
        self._lo_sections = None
        self._i_position = None

    def __iter__(self):
        if len(self._do_sections) > 0:

            self._i_position = 0
            self._lo_sections = []

            for u_section, o_section in self._do_sections.iteritems():
                self._lo_sections.append(o_section)

            self._lo_sections.sort(key=lambda x: x.u_name)

        return self

    def next(self):
        if (self._i_position is not None) and (self._i_position < len(self._do_sections)):
            self._i_position += 1
            return self._lo_sections[self._i_position - 1]
        else:
            raise StopIteration()

    def __str__(self):
        u_output = '<ParsedIni>\n'

        for o_group in self:
            u_output += '  [%s]\n' % o_group.u_name
            for du_param in o_group:
                u_output += '    %s = %s\n' % (du_param['name'], du_param['value'])

        return u_output

    def _add_section(self, u_section, o_section):
        # It doesn't make much sense for me right now to store sections without data in it. But maybe there are programs
        # out there that check that a particular section exists, even when it's empty. For that reason I keep this
        # comment here.
        if o_section.number_of_params() > 0:
            self._do_sections[u_section] = o_section

    def import_from_ini(self, o_new_ini):
        """
        Method to import the content of other ParsedIni object

        :param o_new_ini: ParsedIni object to import.

        :return: NOthing
        """

        for o_new_section in o_new_ini:
            for d_new_param in o_new_section:
                #print o_new_section.u_name, d_new_param
                self.set_param(o_new_section.u_name, d_new_param['name'], d_new_param['value'])

    def load_from_disk(self, u_file):
        """
        Function to parse an ini file. All the information will be read as plain text, so, after using this object, you
        should convert the strings to integers, floats, etc... in case you needed the information in those formats.

        Notice this method ignores all the comments contained in the file. This means you'll lose permanently all the
        coments if you save the ParsedIni to the same ini file you read in first place.

        :param u_file: file object where the information is gathered from.o_file

        input data example:
            [Main]
            a = 14
            b = 56
            [Screen]
            w = 640
        """

        if os.path.isfile(u_file):

            o_file = open(u_file, 'r')

            # Initialization
            u_section = ''
            o_section = _IniSection(u_section)

            for u_line in o_file:
                # again, I should figure a way to avoid explicit encoding format
                u_line = u_line.decode('utf8')

                # Cleaning empty spaces around the real content
                u_line = u_line.strip()

                # cleaning out comments in the ini
                u_line = u_line.partition(';')[0]

                # todo: improve code because a [ or ] after = could trigger the section and that's a BIG ERROR

                i_start = u_line.find('[')
                i_end = u_line.find(']', i_start)

                # If we found a [...] section at the beginning of the line...
                if i_start == 0 and i_end > 0:
                    # First we store the previous section in the container
                    self._add_section(u_section, o_section)

                    # Then we create the new section object ready to be filled.
                    u_section = u_line[i_start + 1:i_end]
                    o_section = _IniSection(u_section)

                else:
                    if u_line.find('=') != -1:
                        u_field = u_line.partition('=')[0]
                        u_field = u_field.strip()

                        u_value = u_line.partition('=')[2]
                        u_value = u_value.strip()

                        if u_field != '':
                            o_section.add_param(u_field, u_value)

            # After processing all the lines, we append the
            self._add_section(u_section, o_section)

    def get_param(self, s_section, s_param):
        """
        Method for reading the value of a field inside a section.

        :param s_section: Name of the section, identified by square brackets. i.e. For '[menu]', s_section = 'menu'.
            NOTE: s_section is NOT case sensitive. i.e. 'main' and 'Main' are the same section.

        :param s_field: Name of the field, just before =. i.e. For 'stars = 10', s_field = 'stars'. NOTE: s_field is NOT
            case sensitive. i.e. 'Start' and 'start' are the same field.

        :return s_output: Value after =. i.e. For 'stars = 10', s_output = '10' NOTICE IT'S ALWAYS A STRING!
        """

        u_output = None

        if self.has_param(s_section, s_param):
            u_output = self._do_sections[s_section].get_param(s_param)

        return u_output

    def has_param(self, u_section, u_param):
        """
        Method to check if a param exists in the ini. Since can appear in different sections, you must also indicate the
        name of the section.

        :param u_section: Name of the section. i.e. 'main'. NOTE: u_section is NOT case sensitive.

        :param u_param: Name of the param. i.e. 'width'. NOTE: u_param is NOT case sensitive.

        :return: True/False.
        """

        b_has_param = False

        if self.has_section(u_section):
            if self._do_sections[u_section].has_param(u_param):
                b_has_param = True

        return b_has_param

    def has_section(self, u_section):
        """
        Method to check if a section exists in the ini:

        :param u_section: Name of the section. i.e. 'main'. NOTE: s_section is NOT case sensitive.

        :return: True/False.
        """

        b_has_section = False

        if u_section in self._do_sections:
            b_has_section = True

        return b_has_section

    def set_param(self, u_section, u_param, u_value):
        """
        Method for setting a new field/x_value couple inside a section
        """

        # If the section didn't exist previously, it has to be created.
        if not self.has_section(u_section):
            self._do_sections[u_section] = _IniSection(u_section)

        # Then, we don't need to check if the parameter exist. We simply add it's value to the dict.
        self._do_sections[u_section].add_param(u_param, u_value)

    def write_to_disk(self, u_file):
        """
        Method to write the ParsedIni object to disk as a standard ini file.

        :param u_file: Name of the file. i.e. '/home/john/my_config.ini'

        :return: Nothing
        """

        o_output_file = open(u_file, 'w')

        for o_section in self:
            o_output_file.write('[%s]\n' % o_section.u_name)
            for du_param in o_section:
                o_output_file.write('%s = %s\n' % (du_param['name'], du_param['value']))
            o_output_file.write('\n')

        o_output_file.close()


class _IniSection:
    def __init__(self, u_name):
        self.u_name = u_name
        self._du_params = dict()

        self._i_position = None
        self._llu_fields = None

    def __str__(self):
        u_output = '    <IniSection: [%s]>\n' % self.u_name

        lu_fields = self._du_params.keys()
        lu_fields.sort()

        for u_field in lu_fields:
            u_output += '        <Field: %s> %s\n' % (u_field, self._du_params[u_field])

        return u_output

    def __iter__(self):

        # If the dictionary contains at least one element, the position is reset to zero and also a list of lists is
        # built containing the field couples (u_name, u_value) that is ALPHABETICALLY SORTED.
        if len(self._du_params) > 0:
            self._i_position = 0
            self._llu_fields = []
            for u_name, u_value in self._du_params.iteritems():
                self._llu_fields.append((u_name, u_value))
            self._llu_fields.sort()

        else:
            self._i_position = None
            self._llu_fields = None

        return self

    def next(self):
        if (self._i_position is not None) and (self._i_position < len(self._du_params)):
            self._i_position += 1
            return {'name': self._llu_fields[self._i_position - 1][0],
                    'value': self._llu_fields[self._i_position - 1][1]}
        else:
            raise StopIteration()

    def add_param(self, u_name, u_value):
        """
        Method to add a group of properties to an ini file.
        """

        self._du_params[u_name] = u_value

    def get_param(self, u_name):
        """
        Method to obtain the value of a field.
        """

        if self.has_param(u_name):
            u_output = self._du_params[u_name]
        else:
            u_output = u''

        return u_output

    def has_param(self, u_name):
        """
        Method to check if a group of properties contains certain parameter.
        """

        b_has_param = False

        if u_name in self._du_params:
            b_has_param = True

        return b_has_param

    def number_of_params(self):
        """
        Method to return the number of fields stored in the group.
        """

        return len(self._du_params)


#=======================================================================================================================
def list_float(s_string):
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
