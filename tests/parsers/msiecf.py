#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the Microsoft Internet Explorer (MSIE) Cache Files (CF) parser."""

import unittest

from plaso.lib import definitions
from plaso.parsers import msiecf

from tests.parsers import test_lib


class MSIECFParserTest(test_lib.ParserTestCase):
  """Tests for the MSIE Cache Files (MSIECF) parser."""

  def testParse(self):
    """Tests the Parse function."""
    parser = msiecf.MSIECFParser()
    storage_writer = self._ParseFile(['index.dat'], parser)

    # MSIE Cache File information:
    #   Version                         : 5.2
    #   File size                       : 32768 bytes
    #   Number of items                 : 7
    #   Number of recovered items       : 11

    self.assertEqual(storage_writer.number_of_warnings, 0)
    # 7 + 11 records, each with 4 records.
    self.assertEqual(storage_writer.number_of_events, (7 + 11) * 4)

    events = list(storage_writer.GetEvents())

    # Record type             : URL
    # Offset range            : 21376 - 21632 (256)
    # Location                : Visited: testing@http://www.trafficfusionx.com
    #                           /download/tfscrn2/funnycats.exe
    # Primary time            : Jun 23, 2011 18:02:10.066000000
    # Secondary time          : Jun 23, 2011 18:02:10.066000000
    # Expiration time         : Jun 29, 2011 17:55:02
    # Last checked time       : Jun 23, 2011 18:02:12
    # Cache directory index   : -2 (0xfe)

    expected_event_values = {
        'cache_directory_index': -2,
        'cached_file_size': 0,
        'data_type': 'msiecf:url',
        'number_of_hits': 6,
        'offset': 21376,
        'timestamp': '2011-06-23 18:02:10.066000',
        'timestamp_desc': definitions.TIME_DESCRIPTION_LAST_VISITED,
        'url': (
            'Visited: testing@http://www.trafficfusionx.com/download/tfscrn2'
            '/funnycats.exe')}

    self.CheckEventValues(storage_writer, events[8], expected_event_values)

    expected_event_values = {
        'data_type': 'msiecf:url',
        'timestamp': '2011-06-23 18:02:10.066000',
        'timestamp_desc': definitions.TIME_DESCRIPTION_LAST_VISITED}

    self.CheckEventValues(storage_writer, events[9], expected_event_values)

    expected_event_values = {
        'data_type': 'msiecf:url',
        'timestamp': '2011-06-29 17:55:02.000000',
        'timestamp_desc': definitions.TIME_DESCRIPTION_EXPIRATION}

    self.CheckEventValues(storage_writer, events[10], expected_event_values)

    expected_event_values = {
        'data_type': 'msiecf:url',
        'timestamp': '2011-06-23 18:02:12.000000',
        'timestamp_desc': definitions.TIME_DESCRIPTION_LAST_CHECKED}

    self.CheckEventValues(storage_writer, events[11], expected_event_values)

  def testParseLeakAndRedirect(self):
    """Tests the Parse function with leak and redirected records."""
    parser = msiecf.MSIECFParser()
    storage_writer = self._ParseFile(['nfury_index.dat'], parser)
    self.assertEqual(storage_writer.number_of_warnings, 0)

    # MSIE Cache File information:
    #   Version                         : 5.2
    #   File size                       : 491520 bytes
    #   Number of items                 : 1027
    #   Number of recovered items       : 8

    self.assertEqual(storage_writer.number_of_events, 2898)

    events = list(storage_writer.GetEvents())

    expected_event_values = {
        'cache_directory_index': 0,
        'cache_directory_name': 'R6QWCVX4',
        'cached_file_size': 4286,
        'cached_filename': 'favicon[1].ico',
        'data_type': 'msiecf:url',
        'http_headers': (
            'HTTP/1.1 200 OK\r\n'
            'Content-Type: image/x-icon\r\n'
            'ETag: "0922651f38cb1:0",\r\n'
            'X-Powered-By: ASP.NET\r\n'
            'P3P: CP="BUS CUR CONo FIN IVDo ONL OUR PHY SAMo TELo"\r\n'
            'Content-Length: 4286\r\n'
            '\r\n'
            '~U:nfury\r\n'),
        'number_of_hits': 1,
        'timestamp': '2010-11-10 07:54:32.000000',
        'timestamp_desc': definitions.TIME_DESCRIPTION_LAST_CHECKED,
        'url': 'http://col.stc.s-msn.com/br/gbl/lg/csl/favicon.ico'}

    self.CheckEventValues(storage_writer, events[3], expected_event_values)

    expected_event_values = {
        'cache_directory_index': 1,
        'cache_directory_name': 'VUQHQA73',
        'cached_file_size': 1966,
        'cached_filename': 'ADSAdClient31[1].htm',
        'data_type': 'msiecf:leak',
        'recovered': False,
        'timestamp': 0,
        'timestamp_desc': definitions.TIME_DESCRIPTION_NOT_A_TIME}

    self.CheckEventValues(storage_writer, events[16], expected_event_values)

    expected_event_values = {
        'data_type': 'msiecf:redirected',
        'recovered': False,
        'timestamp': 0,
        'timestamp_desc': definitions.TIME_DESCRIPTION_NOT_A_TIME,
        'url': (
            'http://ad.doubleclick.net/ad/N2724.Meebo/B5343067.13;'
            'sz=1x1;pc=[TPAS_ID];ord=2642102')}

    self.CheckEventValues(storage_writer, events[21], expected_event_values)


if __name__ == '__main__':
  unittest.main()
