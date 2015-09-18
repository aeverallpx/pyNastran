from __future__ import unicode_literals, print_function
import unittest
from six import PY2
from codecs import open as codec_open

import os
import pyNastran
from pyNastran.bdf.bdf import BDF

root_path = pyNastran.__path__[0]
test_path = os.path.join(root_path, 'bdf', 'test', 'unit')

log = None
class TestReadWrite(unittest.TestCase):

    def test_write_1(self):
        """
        Tests 1 read method and various write methods
        """
        model = BDF(log=log, debug=False)

        bdf_name = os.path.join(test_path, 'test_mass.dat')
        model.read_bdf(bdf_name)
        model.write_bdf(os.path.join(test_path, 'test_mass1a.out'), size=8)
        model.write_bdf(os.path.join(test_path, 'test_mass2a.out'), size=8)
        msg = model.get_bdf_stats(return_type='list')
        # print('\n'.join(msg))

        model.write_bdf(os.path.join(test_path, 'test_mass1b.out'), size=8, interspersed=False)
        model.write_bdf(os.path.join(test_path, 'test_mass2b.out'), size=8, interspersed=True)
        os.remove(os.path.join(test_path, 'test_mass1a.out'))
        os.remove(os.path.join(test_path, 'test_mass2a.out'))
        os.remove(os.path.join(test_path, 'test_mass1b.out'))
        os.remove(os.path.join(test_path, 'test_mass2b.out'))

    def test_punch_1(self):
        """
        Tests punch file reading
        """
        model = BDF(debug=False)
        bdf_name = os.path.join(test_path, 'include_dir', 'include_alt.inc')
        model.read_bdf(bdf_name, xref=False, punch=True)

        model2 = BDF(debug=False)
        #bdf_name = os.path.join(test_path, 'include_dir', 'include.inc')
        model2.read_bdf(bdf_name, xref=False, punch=True)

    def test_read_include_dir_1(self):
        """
        Tests various read methods using various include files
        """
        # fails correctly
        model = BDF(debug=False)
        bdf_name = os.path.join(test_path, 'test_include.bdf')
        model.read_bdf(bdf_name, xref=True, punch=False)
        #self.assertRaises(IOError, model.read_bdf, bdf_name, xref=True, punch=False)

        # passes
        full_path = os.path.join(test_path, 'include_dir')
        model2 = BDF(debug=False)
        bdf_filename = 'test_include.bdf'
        if not os.path.exists(bdf_filename):
            bdf_filename = os.path.join(test_path, 'test_include.bdf')
        model2.read_bdf(bdf_filename, xref=True, punch=False)

    def test_enddata_1(self):
        """
        There is an ENDDATA is in the baseline BDF, so None -> ENDDATA
        """
        model = BDF(debug=False)
        full_path = os.path.join(test_path, 'include_dir')
        model2 = BDF(debug=False)

        bdf_filename = 'test_include.bdf'
        if not os.path.exists(bdf_filename):
            bdf_filename = os.path.join(test_path, bdf_filename)
        model2.read_bdf(bdf_filename, xref=True, punch=False)
        for out_filename, is_enddata, write_flag in [
            ('enddata1.bdf', True, None),
            ('enddata2.bdf', True, True),
            ('enddata3.bdf', False, False)]:
            out_filename = os.path.join(test_path, out_filename)
            model2.write_bdf(out_filename=out_filename+'.out', interspersed=True, size=8,
                             is_double=False, enddata=write_flag)
            data = open(out_filename + '.out', 'r').read()
            if is_enddata:
                self.assertTrue('ENDDATA' in data)
            else:
                self.assertFalse('ENDDATA' in data)
            os.remove(out_filename + '.out')

    def test_enddata_2(self):
        """
        There is no ENDDATA is in the baseline BDF, so None -> no ENDDATA
        """
        model = BDF(debug=False)
        full_path = os.path.join(test_path, 'include_dir')
        model2 = BDF(debug=False)
        bdf_name = os.path.join(test_path, 'test_mass.dat')
        model2.read_bdf(bdf_name, xref=True, punch=False)
        for out_filename, is_enddata, write_flag in [
            ('test_mass1.dat', False, None),
            ('test_mass2.dat', True, True),
            ('test_mass3.dat', False, False)]:
            model2.write_bdf(out_filename=out_filename, interspersed=True, size=8,
                             is_double=False, enddata=write_flag)
            data = open(out_filename, 'r').read()
            msg = 'outfilename=%r expected=%r write_flag=%s card_count=%r' % (out_filename, is_enddata, write_flag, model2.card_count.keys())
            if is_enddata:
                self.assertTrue('ENDDATA' in data, msg)
            else:
                self.assertFalse('ENDDATA' in data, msg)
            os.remove(out_filename)

    def test_include_end(self):
        if PY2:
            wb = 'wb'
        else:
            wb = 'w'
        f = open('a.bdf', wb)
        f.write('CEND\n')
        f.write('BEGIN BULK\n')
        f.write('GRID,1,,1.0\n')
        f.write("INCLUDE 'b.bdf'\n\n")

        f = open('b.bdf', wb)
        f.write('GRID,2,,2.0\n')
        f.write("INCLUDE 'c.bdf'\n\n")

        f = open('c.bdf', wb)
        f.write('GRID,3,,3.0\n\n')
        f.write("ENDDATA\n")
        f.close()

        model = BDF(log=log, debug=False)
        model.read_bdf('a.bdf')
        model.write_bdf('a.out.bdf')

        os.remove('a.bdf')
        os.remove('b.bdf')
        os.remove('c.bdf')
        os.remove('a.out.bdf')
        self.assertEqual(len(model.nodes), 3)
        self.assertEqual(model.nnodes, 3, 'nnodes=%s' % model.nnodes)

    def test_include_end_02(self):
        if PY2:
            wb = 'wb'
        else:
            wb = 'w'
        f = open('a.bdf', wb)
        f.write('CEND\n')
        f.write('BEGIN BULK\n')
        f.write('GRID,1,,1.0\n')
        f.write("INCLUDE 'b.bdf'\n\n")
        f.write('GRID,4,,4.0\n')

        f = open('b.bdf', wb)
        f.write('GRID,2,,2.0\n')
        f.write("INCLUDE 'c.bdf'\n\n")
        f.write('GRID,5,,5.0\n')

        f = open('c.bdf', wb)
        f.write('GRID,3,,3.0\n\n')
        f.close()

        model = BDF(log=log, debug=False)
        model.read_bdf('a.bdf')
        model.write_bdf('a.out.bdf')

        os.remove('a.bdf')
        os.remove('b.bdf')
        os.remove('c.bdf')
        os.remove('a.out.bdf')
        self.assertEqual(len(model.nodes), 5)
        self.assertEqual(model.nnodes, 5, 'nnodes=%s' % model.nnodes)

    def test_include_03(self):
        if PY2:
            wb = 'wb'
        else:
            wb = 'w'
        f = open('a.bdf', wb)
        f.write("INCLUDE 'executive_control.inc'\n\n")
        f.write('CEND\n')
        f.write("INCLUDE 'case_control.inc'\n\n")
        f.write('BEGIN BULK\n')
        f.write('GRID,1,,1.0\n')
        f.write("INCLUDE 'b.bdf'\n\n")
        f.write('GRID,4,,4.0\n')

        f = open('executive_control.inc', wb)
        f.write('SOL = 103\n')

        f = open('case_control.inc', wb)
        f.write('DISP = ALL\n')

        f = open('b.bdf', wb)
        f.write('GRID,2,,2.0\n')
        f.write("INCLUDE 'c.bdf'\n\n")
        f.write('GRID,5,,5.0\n')

        f = open('c.bdf', wb)
        f.write('GRID,3,,3.0\n\n')
        f.close()

        model = BDF(log=log, debug=False)
        model.read_bdf('a.bdf')
        model.write_bdf('a.out.bdf')

        os.remove('a.bdf')
        os.remove('b.bdf')
        os.remove('c.bdf')
        os.remove('executive_control.inc')
        os.remove('case_control.inc')

        os.remove('a.out.bdf')
        self.assertEqual(len(model.nodes), 5)
        self.assertEqual(model.nnodes, 5, 'nnodes=%s' % model.nnodes)

    def test_encoding_write(self):

        mesh = BDF()
        mesh.add_card(['GRID', 100000, 0, 43.91715, -29., .8712984], 'GRID')
        mesh.write_bdf('out.bdf')
        lines_expected = [
            '$pyNastran: version=msc',
            '$pyNastran: punch=False',
            '$pyNastran: encoding=ascii',
            '$NODES',
            'GRID      100000        43.91715    -29..8712984',
        ]
        bdf_filename = 'out.bdf'
        with codec_open(bdf_filename, 'r', encoding='ascii') as f:
            lines = f.readlines()
            i = 0
            for line, line_expected in zip(lines, lines_expected):
                line = line.rstrip()
                line_expected = line_expected.rstrip()
                msg = 'The lines are not the same...i=%s\n' % i
                msg += 'line     = %r\n' % line
                msg += 'expected = %r\n' % line_expected
                msg += '-------------\n--Actual--\n%s' % ''.join(lines)
                msg += '-------------\n--Expected--\n%s' % ''.join(lines_expected)
                self.assertEqual(line, line_expected, msg)
                i += 1

    def test_read_bad_01(self):
        model = BDF()
        model.active_filenames = ['fake.file']
        with self.assertRaises(IOError):
            model._open_file('fake.file')

    def test_disable_cards(self):
        bdf_filename = os.path.join(root_path, '..', 'models',
            'solid_bending', 'solid_bending.bdf')
        model = BDF()
        model.disable_cards(['CTETRA'])
        model.read_bdf(bdf_filename)
        assert len(model.elements) == 0, len(model.elements)

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
