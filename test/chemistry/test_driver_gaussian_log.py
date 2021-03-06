# This code is part of Qiskit.
#
# (C) Copyright IBM 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

""" Test Gaussian Log Driver """

import unittest

from test.chemistry import QiskitChemistryTestCase

from qiskit.chemistry.drivers import GaussianLogDriver, GaussianLogResult
from qiskit.chemistry import QiskitChemistryError


class TestDriverGaussianLog(QiskitChemistryTestCase):
    """Gaussian Log Driver tests."""

    def setUp(self):
        super().setUp()
        self.logfile = self.get_resource_path('test_driver_gaussian_log.txt')

    def test_log_driver(self):
        """ Test the driver itself creates log and we can get a result """
        try:
            driver = GaussianLogDriver(
                ['#p B3LYP/6-31g Freq=(Anharm) Int=Ultrafine SCF=VeryTight',
                 '',
                 'CO2 geometry optimization B3LYP/cc-pVTZ',
                 '',
                 '0 1',
                 'C  -0.848629  2.067624  0.160992',
                 'O   0.098816  2.655801 -0.159738',
                 'O  -1.796073  1.479446  0.481721',
                 '',
                 ''
                 ])
            result = driver.run()
            qfc = result.quadratic_force_constants
            expected = [('1', '1', 1409.20235, 1.17003, 0.07515),
                        ('2', '2', 2526.46159, 3.76076, 0.24156),
                        ('3a', '3a', 462.61566, 0.12609, 0.0081),
                        ('3b', '3b', 462.61566, 0.12609, 0.0081)]
            self.assertListEqual(qfc, expected)
        except QiskitChemistryError:
            self.skipTest('GAUSSIAN driver does not appear to be installed')

    # These tests check the gaussian log result and the parsing from a partial log file that is
    # located with the tests so that this aspect of the code can be tested independent of
    # Gaussian 16 being installed.

    def test_gaussian_log_result_file(self):
        """ Test result from file """
        result = GaussianLogResult(self.logfile)
        with open(self.logfile) as file:
            lines = file.read().split('\n')

        with self.subTest('Check list of lines'):
            self.assertListEqual(result.log, lines)

        with self.subTest('Check as string'):
            line = '\n'.join(lines)
            self.assertEqual(str(result), line)

    def test_gaussian_log_result_list(self):
        """ Test result from list of strings """
        with open(self.logfile) as file:
            lines = file.read().split('\n')
        result = GaussianLogResult(lines)
        self.assertListEqual(result.log, lines)

    def test_gaussian_log_result_string(self):
        """ Test result from string """
        with open(self.logfile) as file:
            line = file.read()
        result = GaussianLogResult(line)
        self.assertListEqual(result.log, line.split('\n'))

    def test_quadratic_force_constants(self):
        """ Test quadratic force constants """
        result = GaussianLogResult(self.logfile)
        qfc = result.quadratic_force_constants
        expected = [('1', '1', 1409.20235, 1.17003, 0.07515),
                    ('2', '2', 2526.46159, 3.76076, 0.24156),
                    ('3a', '3a', 462.61566, 0.12609, 0.0081),
                    ('3b', '3b', 462.61566, 0.12609, 0.0081)]
        self.assertListEqual(qfc, expected)

    def test_cubic_force_constants(self):
        """ Test cubic force constants """
        result = GaussianLogResult(self.logfile)
        cfc = result.cubic_force_constants
        expected = [('1', '1', '1', -260.36071, -1.39757, -0.0475),
                    ('2', '2', '1', -498.9444, -4.80163, -0.1632),
                    ('3a', '3a', '1', 239.87769, 0.4227, 0.01437),
                    ('3a', '3b', '1', 74.25095, 0.13084, 0.00445),
                    ('3b', '3b', '1', 12.93985, 0.0228, 0.00078)]
        self.assertListEqual(cfc, expected)

    def test_quartic_force_constants(self):
        """ Test quartic force constants """
        result = GaussianLogResult(self.logfile)
        qfc = result.quartic_force_constants
        expected = [('1', '1', '1', '1', 40.39063, 1.40169, 0.02521),
                    ('2', '2', '1', '1', 79.08068, 4.92017, 0.0885),
                    ('2', '2', '2', '2', 154.78015, 17.26491, 0.31053),
                    ('3a', '3a', '1', '1', -67.10879, -0.76453, -0.01375),
                    ('3b', '3b', '1', '1', -67.10879, -0.76453, -0.01375),
                    ('3a', '3a', '2', '2', -163.29426, -3.33524, -0.05999),
                    ('3b', '3b', '2', '2', -163.29426, -3.33524, -0.05999),
                    ('3a', '3a', '3a', '3a', 220.54851, 0.82484, 0.01484),
                    ('3a', '3a', '3a', '3b', 66.77089, 0.24972, 0.00449),
                    ('3a', '3a', '3b', '3b', 117.26759, 0.43857, 0.00789),
                    ('3a', '3b', '3b', '3b', -66.77088, -0.24972, -0.00449),
                    ('3b', '3b', '3b', '3b', 220.54851, 0.82484, 0.01484)]
        self.assertListEqual(qfc, expected)

    def test_compute_modes(self):
        """ Test the internal function that is computing modes """
        result = GaussianLogResult(self.logfile)
        modes = result._compute_modes()
        expected = [[352.3005875, 2, 2],
                    [-352.3005875, -2, -2],
                    [631.6153975, 1, 1],
                    [-631.6153975, -1, -1],
                    [115.653915, 4, 4],
                    [-115.653915, -4, -4],
                    [115.653915, 3, 3],
                    [-115.653915, -3, -3],
                    [-15.341901966295344, 2, 2, 2],
                    [-88.2017421687633, 1, 1, 2],
                    [42.40478531359112, 4, 4, 2],
                    [26.25167512727164, 4, 3, 2],
                    [2.2874639206341865, 3, 3, 2],
                    [0.4207357291666667, 2, 2, 2, 2],
                    [4.9425425, 1, 1, 2, 2],
                    [1.6122932291666665, 1, 1, 1, 1],
                    [-4.194299375, 4, 4, 2, 2],
                    [-4.194299375, 3, 3, 2, 2],
                    [-10.20589125, 4, 4, 1, 1],
                    [-10.20589125, 3, 3, 1, 1],
                    [2.2973803125, 4, 4, 4, 4],
                    [2.7821204166666664, 4, 4, 4, 3],
                    [7.329224375, 4, 4, 3, 3],
                    [-2.7821200000000004, 4, 3, 3, 3],
                    [2.2973803125, 3, 3, 3, 3]
                    ]
        for i, entry in enumerate(modes):
            msg = "mode[{}]={} does not match expected {}".format(i, entry, expected[i])
            self.assertAlmostEqual(entry[0], expected[i][0], msg=msg)
            self.assertListEqual(entry[1:], expected[i][1:], msg=msg)

    def test_harmonic_modes(self):
        """ Test harmonic modes """
        result = GaussianLogResult(self.logfile)
        hmodes = result.compute_harmonic_modes(num_modals=3)
        expected = [[([[0, 0, 0]], 1268.0676746875001),
                     ([[0, 0, 2]], 13.68076170725888),
                     ([[0, 1, 1]], 3813.8767834375008),
                     ([[0, 2, 0]], 13.68076170725888),
                     ([[0, 2, 2]], 6379.033410937501),
                     ([[1, 0, 0]], 705.8633821875002),
                     ([[1, 0, 1]], -46.025705898886045),
                     ([[1, 0, 2]], 3.5700610461746014),
                     ([[1, 1, 0]], -46.025705898886045),
                     ([[1, 1, 1]], 2120.1145609375008),
                     ([[1, 1, 2]], -130.180355),
                     ([[1, 2, 0]], 3.5700610461746014),
                     ([[1, 2, 1]], -130.180355),
                     ([[1, 2, 2]], 3539.4145684375007),
                     ([[2, 0, 0]], 238.19997093750004),
                     ([[2, 0, 2]], 19.493918375198643),
                     ([[2, 1, 1]], 728.3841946875002),
                     ([[2, 2, 0]], 19.493918375198643),
                     ([[2, 2, 2]], 1246.1369821875003),
                     ([[3, 0, 0]], 238.19997093750004),
                     ([[3, 0, 2]], 19.493918375198643),
                     ([[3, 1, 1]], 728.3841946875002),
                     ([[3, 2, 0]], 19.493918375198643),
                     ([[3, 2, 2]], 1246.1369821875003)],
                    [([[0, 0, 0], [1, 0, 0]], 4.942542500000002),
                     ([[0, 0, 0], [1, 0, 1]], -88.20174216876333),
                     ([[0, 0, 0], [1, 0, 2]], 6.989810636105426),
                     ([[0, 0, 0], [1, 1, 0]], -88.20174216876333),
                     ([[0, 0, 0], [1, 1, 1]], 14.827627500000007),
                     ([[0, 0, 0], [1, 1, 2]], -124.73610000000002),
                     ([[0, 0, 0], [1, 2, 0]], 6.989810636105426),
                     ([[0, 0, 0], [1, 2, 1]], -124.73610000000002),
                     ([[0, 0, 0], [1, 2, 2]], 24.71271250000001),
                     ([[0, 0, 2], [1, 0, 0]], 6.989810636105426),
                     ([[0, 0, 2], [1, 0, 1]], -124.73610000000005),
                     ([[0, 0, 2], [1, 0, 2]], 9.885085000000004),
                     ([[0, 0, 2], [1, 1, 0]], -124.73610000000005),
                     ([[0, 0, 2], [1, 1, 1]], 20.96943190831628),
                     ([[0, 0, 2], [1, 1, 2]], -176.40348433752666),
                     ([[0, 0, 2], [1, 2, 0]], 9.885085000000004),
                     ([[0, 0, 2], [1, 2, 1]], -176.40348433752666),
                     ([[0, 0, 2], [1, 2, 2]], 34.94905318052713),
                     ([[0, 1, 1], [1, 0, 0]], 14.827627500000007),
                     ([[0, 1, 1], [1, 0, 1]], -264.60522650629),
                     ([[0, 1, 1], [1, 0, 2]], 20.96943190831628),
                     ([[0, 1, 1], [1, 1, 0]], -264.60522650629),
                     ([[0, 1, 1], [1, 1, 1]], 44.482882500000024),
                     ([[0, 1, 1], [1, 1, 2]], -374.20830000000007),
                     ([[0, 1, 1], [1, 2, 0]], 20.96943190831628),
                     ([[0, 1, 1], [1, 2, 1]], -374.20830000000007),
                     ([[0, 1, 1], [1, 2, 2]], 74.13813750000003),
                     ([[0, 2, 0], [1, 0, 0]], 6.989810636105426),
                     ([[0, 2, 0], [1, 0, 1]], -124.73610000000005),
                     ([[0, 2, 0], [1, 0, 2]], 9.885085000000004),
                     ([[0, 2, 0], [1, 1, 0]], -124.73610000000005),
                     ([[0, 2, 0], [1, 1, 1]], 20.96943190831628),
                     ([[0, 2, 0], [1, 1, 2]], -176.40348433752666),
                     ([[0, 2, 0], [1, 2, 0]], 9.885085000000004),
                     ([[0, 2, 0], [1, 2, 1]], -176.40348433752666),
                     ([[0, 2, 0], [1, 2, 2]], 34.94905318052713),
                     ([[0, 2, 2], [1, 0, 0]], 24.712712500000013),
                     ([[0, 2, 2], [1, 0, 1]], -441.0087108438167),
                     ([[0, 2, 2], [1, 0, 2]], 34.94905318052713),
                     ([[0, 2, 2], [1, 1, 0]], -441.0087108438167),
                     ([[0, 2, 2], [1, 1, 1]], 74.13813750000004),
                     ([[0, 2, 2], [1, 1, 2]], -623.6805),
                     ([[0, 2, 2], [1, 2, 0]], 34.94905318052713),
                     ([[0, 2, 2], [1, 2, 1]], -623.6805),
                     ([[0, 2, 2], [1, 2, 2]], 123.56356250000005),
                     ([[2, 0, 0], [0, 0, 0]], -10.205891250000004),
                     ([[2, 0, 0], [0, 0, 2]], -14.433309821854907),
                     ([[2, 0, 0], [0, 1, 1]], -30.617673750000016),
                     ([[2, 0, 0], [0, 2, 0]], -14.433309821854907),
                     ([[2, 0, 0], [0, 2, 2]], -51.029456250000024),
                     ([[2, 0, 0], [1, 0, 0]], -4.194299375000002),
                     ([[2, 0, 0], [1, 0, 1]], 2.2874639206341874),
                     ([[2, 0, 0], [1, 0, 2]], -5.931635060777999),
                     ([[2, 0, 0], [1, 1, 0]], 2.2874639206341874),
                     ([[2, 0, 0], [1, 1, 1]], -12.582898125000007),
                     ([[2, 0, 0], [1, 1, 2]], 3.2349625000000004),
                     ([[2, 0, 0], [1, 2, 0]], -5.931635060777999),
                     ([[2, 0, 0], [1, 2, 1]], 3.2349625000000004),
                     ([[2, 0, 0], [1, 2, 2]], -20.971496875000007),
                     ([[2, 0, 2], [0, 0, 0]], -14.433309821854907),
                     ([[2, 0, 2], [0, 0, 2]], -20.411782500000008),
                     ([[2, 0, 2], [0, 1, 1]], -43.29992946556472),
                     ([[2, 0, 2], [0, 2, 0]], -20.411782500000008),
                     ([[2, 0, 2], [0, 2, 2]], -72.16654910927453),
                     ([[2, 0, 2], [1, 0, 0]], -5.931635060777999),
                     ([[2, 0, 2], [1, 0, 1]], 3.2349625000000013),
                     ([[2, 0, 2], [1, 0, 2]], -8.388598750000003),
                     ([[2, 0, 2], [1, 1, 0]], 3.2349625000000013),
                     ([[2, 0, 2], [1, 1, 1]], -17.794905182334),
                     ([[2, 0, 2], [1, 1, 2]], 4.574927841268375),
                     ([[2, 0, 2], [1, 2, 0]], -8.388598750000003),
                     ([[2, 0, 2], [1, 2, 1]], 4.574927841268375),
                     ([[2, 0, 2], [1, 2, 2]], -29.658175303889994),
                     ([[2, 1, 1], [0, 0, 0]], -30.61767375000002),
                     ([[2, 1, 1], [0, 0, 2]], -43.29992946556473),
                     ([[2, 1, 1], [0, 1, 1]], -91.85302125000007),
                     ([[2, 1, 1], [0, 2, 0]], -43.29992946556473),
                     ([[2, 1, 1], [0, 2, 2]], -153.0883687500001),
                     ([[2, 1, 1], [1, 0, 0]], -12.582898125000007),
                     ([[2, 1, 1], [1, 0, 1]], 6.862391761902563),
                     ([[2, 1, 1], [1, 0, 2]], -17.794905182334),
                     ([[2, 1, 1], [1, 1, 0]], 6.862391761902563),
                     ([[2, 1, 1], [1, 1, 1]], -37.74869437500002),
                     ([[2, 1, 1], [1, 1, 2]], 9.704887500000002),
                     ([[2, 1, 1], [1, 2, 0]], -17.794905182334),
                     ([[2, 1, 1], [1, 2, 1]], 9.704887500000002),
                     ([[2, 1, 1], [1, 2, 2]], -62.91449062500003),
                     ([[2, 2, 0], [0, 0, 0]], -14.433309821854907),
                     ([[2, 2, 0], [0, 0, 2]], -20.411782500000008),
                     ([[2, 2, 0], [0, 1, 1]], -43.29992946556472),
                     ([[2, 2, 0], [0, 2, 0]], -20.411782500000008),
                     ([[2, 2, 0], [0, 2, 2]], -72.16654910927453),
                     ([[2, 2, 0], [1, 0, 0]], -5.931635060777999),
                     ([[2, 2, 0], [1, 0, 1]], 3.2349625000000013),
                     ([[2, 2, 0], [1, 0, 2]], -8.388598750000003),
                     ([[2, 2, 0], [1, 1, 0]], 3.2349625000000013),
                     ([[2, 2, 0], [1, 1, 1]], -17.794905182334),
                     ([[2, 2, 0], [1, 1, 2]], 4.574927841268375),
                     ([[2, 2, 0], [1, 2, 0]], -8.388598750000003),
                     ([[2, 2, 0], [1, 2, 1]], 4.574927841268375),
                     ([[2, 2, 0], [1, 2, 2]], -29.658175303889994),
                     ([[2, 2, 2], [0, 0, 0]], -51.029456250000024),
                     ([[2, 2, 2], [0, 0, 2]], -72.16654910927453),
                     ([[2, 2, 2], [0, 1, 1]], -153.0883687500001),
                     ([[2, 2, 2], [0, 2, 0]], -72.16654910927453),
                     ([[2, 2, 2], [0, 2, 2]], -255.1472812500001),
                     ([[2, 2, 2], [1, 0, 0]], -20.971496875000007),
                     ([[2, 2, 2], [1, 0, 1]], 11.437319603170936),
                     ([[2, 2, 2], [1, 0, 2]], -29.65817530388999),
                     ([[2, 2, 2], [1, 1, 0]], 11.437319603170936),
                     ([[2, 2, 2], [1, 1, 1]], -62.91449062500003),
                     ([[2, 2, 2], [1, 1, 2]], 16.1748125),
                     ([[2, 2, 2], [1, 2, 0]], -29.65817530388999),
                     ([[2, 2, 2], [1, 2, 1]], 16.1748125),
                     ([[2, 2, 2], [1, 2, 2]], -104.85748437500004),
                     ([[3, 0, 0], [0, 0, 0]], -10.205891250000004),
                     ([[3, 0, 0], [0, 0, 2]], -14.433309821854907),
                     ([[3, 0, 0], [0, 1, 1]], -30.617673750000016),
                     ([[3, 0, 0], [0, 2, 0]], -14.433309821854907),
                     ([[3, 0, 0], [0, 2, 2]], -51.029456250000024),
                     ([[3, 0, 0], [1, 0, 0]], -4.194299375000002),
                     ([[3, 0, 0], [1, 0, 1]], 42.404785313591134),
                     ([[3, 0, 0], [1, 0, 2]], -5.931635060777999),
                     ([[3, 0, 0], [1, 1, 0]], 42.404785313591134),
                     ([[3, 0, 0], [1, 1, 1]], -12.582898125000007),
                     ([[3, 0, 0], [1, 1, 2]], 59.969422500000015),
                     ([[3, 0, 0], [1, 2, 0]], -5.931635060777999),
                     ([[3, 0, 0], [1, 2, 1]], 59.969422500000015),
                     ([[3, 0, 0], [1, 2, 2]], -20.971496875000007),
                     ([[3, 0, 0], [2, 0, 0]], 7.3292243750000035),
                     ([[3, 0, 0], [2, 0, 2]], 10.365088512800476),
                     ([[3, 0, 0], [2, 1, 1]], 21.98767312500001),
                     ([[3, 0, 0], [2, 2, 0]], 10.365088512800476),
                     ([[3, 0, 0], [2, 2, 2]], 36.64612187500001),
                     ([[3, 0, 1], [2, 0, 1]], 1.2499999986204102e-06),
                     ([[3, 0, 1], [2, 1, 0]], 1.2499999986204102e-06),
                     ([[3, 0, 1], [2, 1, 2]], -11.803533740681361),
                     ([[3, 0, 1], [2, 2, 1]], -11.803533740681361),
                     ([[3, 0, 2], [0, 0, 0]], -14.433309821854907),
                     ([[3, 0, 2], [0, 0, 2]], -20.411782500000008),
                     ([[3, 0, 2], [0, 1, 1]], -43.29992946556472),
                     ([[3, 0, 2], [0, 2, 0]], -20.411782500000008),
                     ([[3, 0, 2], [0, 2, 2]], -72.16654910927453),
                     ([[3, 0, 2], [1, 0, 0]], -5.931635060777999),
                     ([[3, 0, 2], [1, 0, 1]], 59.96942250000003),
                     ([[3, 0, 2], [1, 0, 2]], -8.388598750000003),
                     ([[3, 0, 2], [1, 1, 0]], 59.96942250000003),
                     ([[3, 0, 2], [1, 1, 1]], -17.794905182334),
                     ([[3, 0, 2], [1, 1, 2]], 84.80957062718227),
                     ([[3, 0, 2], [1, 2, 0]], -8.388598750000003),
                     ([[3, 0, 2], [1, 2, 1]], 84.80957062718227),
                     ([[3, 0, 2], [1, 2, 2]], -29.658175303889994),
                     ([[3, 0, 2], [2, 0, 0]], 10.365088512800474),
                     ([[3, 0, 2], [2, 0, 2]], 14.658448750000005),
                     ([[3, 0, 2], [2, 1, 1]], 31.095265538401428),
                     ([[3, 0, 2], [2, 2, 0]], 14.658448750000005),
                     ([[3, 0, 2], [2, 2, 2]], 51.82544256400237),
                     ([[3, 1, 0], [2, 0, 1]], 1.2499999986204102e-06),
                     ([[3, 1, 0], [2, 1, 0]], 1.2499999986204102e-06),
                     ([[3, 1, 0], [2, 1, 2]], -11.803533740681361),
                     ([[3, 1, 0], [2, 2, 1]], -11.803533740681361),
                     ([[3, 1, 1], [0, 0, 0]], -30.61767375000002),
                     ([[3, 1, 1], [0, 0, 2]], -43.29992946556473),
                     ([[3, 1, 1], [0, 1, 1]], -91.85302125000007),
                     ([[3, 1, 1], [0, 2, 0]], -43.29992946556473),
                     ([[3, 1, 1], [0, 2, 2]], -153.0883687500001),
                     ([[3, 1, 1], [1, 0, 0]], -12.582898125000007),
                     ([[3, 1, 1], [1, 0, 1]], 127.21435594077343),
                     ([[3, 1, 1], [1, 0, 2]], -17.794905182334),
                     ([[3, 1, 1], [1, 1, 0]], 127.21435594077343),
                     ([[3, 1, 1], [1, 1, 1]], -37.74869437500002),
                     ([[3, 1, 1], [1, 1, 2]], 179.90826750000008),
                     ([[3, 1, 1], [1, 2, 0]], -17.794905182334),
                     ([[3, 1, 1], [1, 2, 1]], 179.90826750000008),
                     ([[3, 1, 1], [1, 2, 2]], -62.91449062500003),
                     ([[3, 1, 1], [2, 0, 0]], 21.98767312500001),
                     ([[3, 1, 1], [2, 0, 2]], 31.09526553840143),
                     ([[3, 1, 1], [2, 1, 1]], 65.96301937500004),
                     ([[3, 1, 1], [2, 2, 0]], 31.09526553840143),
                     ([[3, 1, 1], [2, 2, 2]], 109.93836562500006),
                     ([[3, 1, 2], [2, 0, 1]], 11.80353904398221),
                     ([[3, 1, 2], [2, 1, 0]], 11.80353904398221),
                     ([[3, 1, 2], [2, 1, 2]], 4.999999994481641e-06),
                     ([[3, 1, 2], [2, 2, 1]], 4.999999994481641e-06),
                     ([[3, 2, 0], [0, 0, 0]], -14.433309821854907),
                     ([[3, 2, 0], [0, 0, 2]], -20.411782500000008),
                     ([[3, 2, 0], [0, 1, 1]], -43.29992946556472),
                     ([[3, 2, 0], [0, 2, 0]], -20.411782500000008),
                     ([[3, 2, 0], [0, 2, 2]], -72.16654910927453),
                     ([[3, 2, 0], [1, 0, 0]], -5.931635060777999),
                     ([[3, 2, 0], [1, 0, 1]], 59.96942250000003),
                     ([[3, 2, 0], [1, 0, 2]], -8.388598750000003),
                     ([[3, 2, 0], [1, 1, 0]], 59.96942250000003),
                     ([[3, 2, 0], [1, 1, 1]], -17.794905182334),
                     ([[3, 2, 0], [1, 1, 2]], 84.80957062718227),
                     ([[3, 2, 0], [1, 2, 0]], -8.388598750000003),
                     ([[3, 2, 0], [1, 2, 1]], 84.80957062718227),
                     ([[3, 2, 0], [1, 2, 2]], -29.658175303889994),
                     ([[3, 2, 0], [2, 0, 0]], 10.365088512800474),
                     ([[3, 2, 0], [2, 0, 2]], 14.658448750000005),
                     ([[3, 2, 0], [2, 1, 1]], 31.095265538401428),
                     ([[3, 2, 0], [2, 2, 0]], 14.658448750000005),
                     ([[3, 2, 0], [2, 2, 2]], 51.82544256400237),
                     ([[3, 2, 1], [2, 0, 1]], 11.80353904398221),
                     ([[3, 2, 1], [2, 1, 0]], 11.80353904398221),
                     ([[3, 2, 1], [2, 1, 2]], 4.999999994481641e-06),
                     ([[3, 2, 1], [2, 2, 1]], 4.999999994481641e-06),
                     ([[3, 2, 2], [0, 0, 0]], -51.029456250000024),
                     ([[3, 2, 2], [0, 0, 2]], -72.16654910927453),
                     ([[3, 2, 2], [0, 1, 1]], -153.0883687500001),
                     ([[3, 2, 2], [0, 2, 0]], -72.16654910927453),
                     ([[3, 2, 2], [0, 2, 2]], -255.1472812500001),
                     ([[3, 2, 2], [1, 0, 0]], -20.971496875000007),
                     ([[3, 2, 2], [1, 0, 1]], 212.0239265679557),
                     ([[3, 2, 2], [1, 0, 2]], -29.65817530388999),
                     ([[3, 2, 2], [1, 1, 0]], 212.0239265679557),
                     ([[3, 2, 2], [1, 1, 1]], -62.91449062500003),
                     ([[3, 2, 2], [1, 1, 2]], 299.8471125000001),
                     ([[3, 2, 2], [1, 2, 0]], -29.65817530388999),
                     ([[3, 2, 2], [1, 2, 1]], 299.8471125000001),
                     ([[3, 2, 2], [1, 2, 2]], -104.85748437500004),
                     ([[3, 2, 2], [2, 0, 0]], 36.64612187500001),
                     ([[3, 2, 2], [2, 0, 2]], 51.82544256400237),
                     ([[3, 2, 2], [2, 1, 1]], 109.93836562500005),
                     ([[3, 2, 2], [2, 2, 0]], 51.82544256400237),
                     ([[3, 2, 2], [2, 2, 2]], 183.23060937500006)],
                    [([[3, 0, 1], [2, 0, 1], [1, 0, 1]], 26.25167512727166),
                     ([[3, 0, 1], [2, 0, 1], [1, 1, 0]], 26.25167512727166),
                     ([[3, 0, 1], [2, 0, 1], [1, 1, 2]], 37.12547500000002),
                     ([[3, 0, 1], [2, 0, 1], [1, 2, 1]], 37.12547500000002),
                     ([[3, 0, 1], [2, 1, 0], [1, 0, 1]], 26.25167512727166),
                     ([[3, 0, 1], [2, 1, 0], [1, 1, 0]], 26.25167512727166),
                     ([[3, 0, 1], [2, 1, 0], [1, 1, 2]], 37.12547500000002),
                     ([[3, 0, 1], [2, 1, 0], [1, 2, 1]], 37.12547500000002),
                     ([[3, 0, 1], [2, 1, 2], [1, 0, 1]], 37.125475000000016),
                     ([[3, 0, 1], [2, 1, 2], [1, 1, 0]], 37.125475000000016),
                     ([[3, 0, 1], [2, 1, 2], [1, 1, 2]], 52.5033502545433),
                     ([[3, 0, 1], [2, 1, 2], [1, 2, 1]], 52.5033502545433),
                     ([[3, 0, 1], [2, 2, 1], [1, 0, 1]], 37.125475000000016),
                     ([[3, 0, 1], [2, 2, 1], [1, 1, 0]], 37.125475000000016),
                     ([[3, 0, 1], [2, 2, 1], [1, 1, 2]], 52.5033502545433),
                     ([[3, 0, 1], [2, 2, 1], [1, 2, 1]], 52.5033502545433),
                     ([[3, 1, 0], [2, 0, 1], [1, 0, 1]], 26.25167512727166),
                     ([[3, 1, 0], [2, 0, 1], [1, 1, 0]], 26.25167512727166),
                     ([[3, 1, 0], [2, 0, 1], [1, 1, 2]], 37.12547500000002),
                     ([[3, 1, 0], [2, 0, 1], [1, 2, 1]], 37.12547500000002),
                     ([[3, 1, 0], [2, 1, 0], [1, 0, 1]], 26.25167512727166),
                     ([[3, 1, 0], [2, 1, 0], [1, 1, 0]], 26.25167512727166),
                     ([[3, 1, 0], [2, 1, 0], [1, 1, 2]], 37.12547500000002),
                     ([[3, 1, 0], [2, 1, 0], [1, 2, 1]], 37.12547500000002),
                     ([[3, 1, 0], [2, 1, 2], [1, 0, 1]], 37.125475000000016),
                     ([[3, 1, 0], [2, 1, 2], [1, 1, 0]], 37.125475000000016),
                     ([[3, 1, 0], [2, 1, 2], [1, 1, 2]], 52.5033502545433),
                     ([[3, 1, 0], [2, 1, 2], [1, 2, 1]], 52.5033502545433),
                     ([[3, 1, 0], [2, 2, 1], [1, 0, 1]], 37.125475000000016),
                     ([[3, 1, 0], [2, 2, 1], [1, 1, 0]], 37.125475000000016),
                     ([[3, 1, 0], [2, 2, 1], [1, 1, 2]], 52.5033502545433),
                     ([[3, 1, 0], [2, 2, 1], [1, 2, 1]], 52.5033502545433),
                     ([[3, 1, 2], [2, 0, 1], [1, 0, 1]], 37.125475000000016),
                     ([[3, 1, 2], [2, 0, 1], [1, 1, 0]], 37.125475000000016),
                     ([[3, 1, 2], [2, 0, 1], [1, 1, 2]], 52.5033502545433),
                     ([[3, 1, 2], [2, 0, 1], [1, 2, 1]], 52.5033502545433),
                     ([[3, 1, 2], [2, 1, 0], [1, 0, 1]], 37.125475000000016),
                     ([[3, 1, 2], [2, 1, 0], [1, 1, 0]], 37.125475000000016),
                     ([[3, 1, 2], [2, 1, 0], [1, 1, 2]], 52.5033502545433),
                     ([[3, 1, 2], [2, 1, 0], [1, 2, 1]], 52.5033502545433),
                     ([[3, 1, 2], [2, 1, 2], [1, 0, 1]], 52.5033502545433),
                     ([[3, 1, 2], [2, 1, 2], [1, 1, 0]], 52.5033502545433),
                     ([[3, 1, 2], [2, 1, 2], [1, 1, 2]], 74.25095000000002),
                     ([[3, 1, 2], [2, 1, 2], [1, 2, 1]], 74.25095000000002),
                     ([[3, 1, 2], [2, 2, 1], [1, 0, 1]], 52.5033502545433),
                     ([[3, 1, 2], [2, 2, 1], [1, 1, 0]], 52.5033502545433),
                     ([[3, 1, 2], [2, 2, 1], [1, 1, 2]], 74.25095000000002),
                     ([[3, 1, 2], [2, 2, 1], [1, 2, 1]], 74.25095000000002),
                     ([[3, 2, 1], [2, 0, 1], [1, 0, 1]], 37.125475000000016),
                     ([[3, 2, 1], [2, 0, 1], [1, 1, 0]], 37.125475000000016),
                     ([[3, 2, 1], [2, 0, 1], [1, 1, 2]], 52.5033502545433),
                     ([[3, 2, 1], [2, 0, 1], [1, 2, 1]], 52.5033502545433),
                     ([[3, 2, 1], [2, 1, 0], [1, 0, 1]], 37.125475000000016),
                     ([[3, 2, 1], [2, 1, 0], [1, 1, 0]], 37.125475000000016),
                     ([[3, 2, 1], [2, 1, 0], [1, 1, 2]], 52.5033502545433),
                     ([[3, 2, 1], [2, 1, 0], [1, 2, 1]], 52.5033502545433),
                     ([[3, 2, 1], [2, 1, 2], [1, 0, 1]], 52.5033502545433),
                     ([[3, 2, 1], [2, 1, 2], [1, 1, 0]], 52.5033502545433),
                     ([[3, 2, 1], [2, 1, 2], [1, 1, 2]], 74.25095000000002),
                     ([[3, 2, 1], [2, 1, 2], [1, 2, 1]], 74.25095000000002),
                     ([[3, 2, 1], [2, 2, 1], [1, 0, 1]], 52.5033502545433),
                     ([[3, 2, 1], [2, 2, 1], [1, 1, 0]], 52.5033502545433),
                     ([[3, 2, 1], [2, 2, 1], [1, 1, 2]], 74.25095000000002),
                     ([[3, 2, 1], [2, 2, 1], [1, 2, 1]], 74.25095000000002)]]

        for i, hmode in enumerate(hmodes):
            for j, entry in enumerate(hmode):
                msg = "mode[{}][{}]={} does not match expected {}".format(i, j, entry,
                                                                          expected[i][j])
                self.assertListEqual(entry[0], expected[i][j][0], msg=msg)
                self.assertAlmostEqual(entry[1], expected[i][j][1], msg=msg)

    # This is just a dummy test at present to print out the stages of the computation
    # to get to the arrays that will be used to compute input for Bosonic Operator
    def _test_modes(self):
        """ Placeholder """
        result = GaussianLogResult(self.logfile)
        print("---------- OUT file equivalent ------------")
        print(result._compute_modes())
        print("---------- HAM file equivalent ------------")
        print(result.compute_harmonic_modes(num_modals=3))


if __name__ == '__main__':
    unittest.main()
