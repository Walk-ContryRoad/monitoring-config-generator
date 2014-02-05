import os
import unittest


from mock import patch


from TestLogger import init_test_logger

os.environ['MONITORING_CONFIG_GENERATOR_CONFIG'] = "testdata/testconfig.yaml"
from monitoring_config_generator.readers import InputReader
from monitoring_config_generator.readers import read_config, read_config_from_file


class Test(unittest.TestCase):

    init_test_logger()

    def test_etag_no_input(self):
        input_reader = InputReader("test.some.domain.yaml", "testDirName")
        input_reader.read_input()
        self.assertEquals(None, input_reader.etag)

    def test_read_file(self):
        host_name = "testhost03.other.domain"
        yaml_filename = host_name + ".yaml"
        cfg_filename = host_name + ".cfg"
        input_dir = "testdata/itest_testhost03_new_format"
        full_input_path = os.path.join(input_dir, yaml_filename)
        output_dir = "testOutputDir"
        full_output_path = os.path.join(output_dir, cfg_filename)
        input_reader = InputReader(full_input_path, output_dir)
        input_reader.read_input()
        self.assertEquals(host_name, input_reader.hostname)
        self.assertEquals(full_input_path, input_reader.filename)
        self.assertEquals(full_output_path, input_reader.output_path)
        self.assertTrue(input_reader.config_changed)
        self.assertTrue(input_reader.is_file)

        # output dir doesn't exist, so there should be no etag
        self.assertEquals(None, input_reader.etag)


ANY_PATH = '/path/to/file'


class TestConfigReaders(unittest.TestCase):

    @patch('monitoring_config_generator.readers.read_config_from_file')
    def test_read_config_calls_read_file_with_file_uri(self, mock_read_config_from_file):
        for i, uri in enumerate([ANY_PATH, 'file://' + ANY_PATH]):
            read_config(uri)
            mock_read_config_from_file.assert_called_with(ANY_PATH)
            self.assertEquals(i + 1, mock_read_config_from_file.call_count)

    @patch('monitoring_config_generator.readers.read_config_from_host')
    def test_read_config_calls_read_file_with_host_uri(self, mock_read_config_from_host):
        for i, uri in enumerate(['http://example.com', 'https://example.com']):
            read_config(uri)
            self.assertEquals(i + 1, mock_read_config_from_host.call_count)

    def test_read_config_raises_exception_with_invalid_uri(self):
        self.assertRaises(ValueError, read_config, 'ftp://example.com')

    @patch('monitoring_config_generator.readers.merge_yaml_files')
    @patch('os.path.getmtime')
    def test_read_config_from_file(self, getmtime_mock, merge_yaml_files_mock):
        ANY_MERGED_YAML = 'any_yaml'
        ANY_MTIME = 123456789.0
        merge_yaml_files_mock.return_value = ANY_MERGED_YAML
        getmtime_mock.return_value = ANY_MTIME
        merged_yaml, etag, mtime = read_config_from_file(ANY_PATH)
        merge_yaml_files_mock.assert_called_once_with(ANY_PATH)
        getmtime_mock.assert_called_once_with(ANY_PATH)
        self.assertEquals(ANY_MERGED_YAML, merged_yaml)
        self.assertEquals(ANY_MTIME, mtime)

