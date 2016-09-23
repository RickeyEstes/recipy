"""
Tests of recipy configuration, provided via recipyrc configuration
files.
"""

# Copyright (c) 2016 University of Edinburgh.

import json
import os
import os.path
import shutil
import tempfile
import pytest

from integration_test import environment
from integration_test import helpers
from integration_test import process
from integration_test import recipy_environment as recipyenv


class TestRecipy:
    """
    Tests of recipy configuration, provided via recipyr configuration
    files.
    """

    SCRIPT_NAME = "run_numpy.py"
    """ Test script assumed to be in same directory as this class. """
    script = ""
    """ Absolute path to test script. """
    directory = ""
    """ Absolute path to temporary directory for these tests. """
    input_file = ""
    """ Absolute path to sample input data file for above script. """
    output_file = ""
    """ Absolute path to sample output data file for above script. """

    @classmethod
    def run_script(cls):
        """
        Run test_script using current Python executable.

        :return: (exit code, standard output and error)
        :rtype: (int, str or unicode)
        """
        return process.execute_and_capture(
            environment.get_python_exe(),
            [TestRecipy.script,
             TestRecipy.input_file,
             TestRecipy.output_file])

    @classmethod
    def setup_class(cls):
        """
        py.test setup function, creates test directory in $TEMP,
        test_input_file path, test_input_file with CSV,
        test_output_file path.
        """
        TestRecipy.script =\
            os.path.join(os.path.dirname(__file__),
                         TestRecipy.SCRIPT_NAME)
        TestRecipy.directory =\
            tempfile.mkdtemp(TestRecipy.__name__)
        TestRecipy.input_file =\
            os.path.join(TestRecipy.directory, "input.csv")
        with open(TestRecipy.input_file, "w") as csv_file:
            csv_file.write("1,4,9,16\n")
            csv_file.write("1,8,27,64\n")
            csv_file.write("\n")
        TestRecipy.output_file =\
            os.path.join(TestRecipy.directory, "output.csv")

    @classmethod
    def teardown_class(cls):
        """
        py.test teardown function, deletes test directory in $TEMP.
        """
        if os.path.isdir(TestRecipy.directory):
            shutil.rmtree(TestRecipy.directory)

    def setup_method(self, method):
        """
        py.test setup function, empties ~/.recipy, deletes recipyrc and
        .recipyrc.

        :param method: Test method
        :type method: function
        """
        helpers.clean_recipy()

    def teardown_method(self, method):
        """
        py.test teardown function, deletes output_file.

        :param method: Test method
        :type method: function
        """
        if os.path.isfile(TestRecipy.output_file):
            os.remove(TestRecipy.output_file)

    def test_no_arguments(self):
        """
        Test "recipy".
        """
        exit_code, stdout = process.execute_and_capture("recipy", [])
        assert exit_code == 1, ("Unexpected exit code " + str(exit_code))
        assert len(stdout) > 0, "Expected stdout"
        helpers.search_regexps(stdout[0], ["Usage:\n"])

    def test_version(self):
        """
        Test "recipy --version".
        """
        exit_code, stdout = process.execute_and_capture(
            "recipy", ["--version"])
        assert exit_code == 0, ("Unexpected exit code " + str(exit_code))
        assert len(stdout) > 0, "Expected stdout"
        helpers.search_regexps(stdout[0], [r"recipy v[0-9]\.[0-9]\.[0-9]"])

    @pytest.mark.parametrize("help_flag", ["-h", "--help"])
    def test_help(self, help_flag):
        """
        Test "recipy -h|--help".
        """
        exit_code, stdout = process.execute_and_capture("recipy", [help_flag])
        assert exit_code == 0, ("Unexpected exit code " + str(exit_code))
        assert len(stdout) > 0, "Expected stdout"
        regexps = [r"recipy - a frictionless provenance tool for Python\n",
                   r"Usage:\n",
                   r"Options:\n"]
        helpers.search_regexps(" ".join(stdout), regexps)

    def test_latest_empty_db(self):
        """
        Test "recipy latest" if no database.
        """
        exit_code, stdout = process.execute_and_capture("recipy", ["latest"])
        assert exit_code == 0, ("Unexpected exit code " + str(exit_code))
        assert len(stdout) > 0
        assert 'Database is empty' in stdout[0]

    def test_latest(self):
        """
        Test "recipy latest".
        """
        exit_code, _ = TestRecipy.run_script()
        assert exit_code == 0, ("Unexpected exit code " + str(exit_code))
        exit_code, stdout = process.execute_and_capture(
            "recipy", ["latest"])
        assert exit_code == 0, ("Unexpected exit code " + str(exit_code))
        regexps = [r"Run ID: .*\n",
                   r"Created by .* on .*\n",
                   r"Ran .* using .*\n",
                   r"Git: commit .*, in .*, with origin .*\n",
                   r"Environment: .*\n",
                   r"Libraries: .*\n",
                   r"Inputs:\n",
                   r"Outputs:\n"]
        helpers.search_regexps(" ".join(stdout), regexps)

    def compare_json_logs(self, log1, log2):
        """
        Compare two recipy JSON logs for equality.

        :param log1: Log
        :type log1: dict
        :param log2: Another log
        :type log2: dict
        :raises AssertionError: if log1 and log2 differ in their keys
        and/or values
        """
        # Convert dates from str or unicode to datetime.datetime.
        for key in ["date", "exit_date"]:
            log1[key] = environment.get_tinydatestr_as_date(log1[key])
            log2[key] = environment.get_tinydatestr_as_date(log2[key])
        assert log1 == log2, "Expected equal logs"

    @pytest.mark.parametrize("json_flag", ["-j", "--json"])
    def test_latest_json(self, json_flag):
        """
        Test "recipy latest [-j|json]".
        """
        exit_code, _ = TestRecipy.run_script()
        assert exit_code == 0, ("Unexpected exit code " + str(exit_code))
        exit_code, stdout = process.execute_and_capture(
            "recipy", ["latest", json_flag])
        assert exit_code == 0, ("Unexpected exit code " + str(exit_code))
        json_log = json.loads(" ".join(stdout))
        db_log, _ = helpers.get_log(recipyenv.get_recipydb())
        self.compare_json_logs(json_log, db_log)

    def test_search_i_unknown(self):
        """
        Test "recipy search -i unknown" if no database.
        """
        exit_code, stdout = process.execute_and_capture(
            "recipy", ["search", "-i", "unknown"])
        assert exit_code == 0, ("Unexpected exit code " + str(exit_code))
        assert len(stdout) > 0
        assert 'No results found' in stdout[0]
