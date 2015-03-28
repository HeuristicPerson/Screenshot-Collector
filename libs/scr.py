#!/usr/local/bin/python
# -*- coding: utf8 -*-


def printh(u_title, i_level=1):
    """
    Funtion to print headings to screen.

    :param u_title: The text to display

    :param i_level: The importance of the title, being 1 the hightest and 3 the lowest

    :return: Nothing.
    """
    print u_title.encode('utf8', 'strict')

    if i_level == 1:
        s_sep_char = '='
    elif i_level == 2:
        s_sep_char = '-'
    elif i_level == 3:
        s_sep_char = '·'
    else:
        raise Exception('Invalid title level "%s"' % str(i_level))

    print s_sep_char * 79
