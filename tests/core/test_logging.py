import os
import unittest
from logging import FileHandler, StreamHandler, getLogger

from py4ai.core.logging import configFromFiles
from py4ai.core.tests.core import TestCase, logTest
from tests import DATA_FOLDER, TMP_FOLDER, clean_tmp_folder, unset_TMP_FOLDER


class TestSetupLogger(TestCase):
    root_logger = getLogger()
    py4ai_logger = getLogger(name="py4ai")

    @classmethod
    def setUpClass(cls) -> None:
        configFromFiles(
            config_files=[os.path.join(DATA_FOLDER, "logging.yml")],
            capture_warnings=True,
            catch_exceptions="except",
        )

    @logTest
    def test_console_logger(self) -> None:
        self.root_logger.info("Example of logging with root logger!")
        self.assertEqual(self.root_logger.name, "root")
        self.assertEqual(self.root_logger.level, 20)
        for h in self.root_logger.handlers:
            self.assertIsInstance(h, StreamHandler)

    @logTest
    def test_file_logger_name(self) -> None:
        self.assertEqual(self.py4ai_logger.name, "py4ai")

    @logTest
    def test_file_logger_handlers(self) -> None:
        self.assertTrue(
            all([isinstance(h, FileHandler) for h in self.py4ai_logger.handlers])
        )

    @logTest
    def test_file_logger_path_creation(self) -> None:
        self.assertTrue(os.path.exists(TMP_FOLDER))
        self.assertTrue(
            all([os.path.exists(h.baseFilename) for h in self.py4ai_logger.handlers])  # type: ignore
        )

    @logTest
    def test_file_logger_overwrite_level(self) -> None:
        self.assertEqual(self.py4ai_logger.level, 20)

    @logTest
    def test_file_logger_dest_file(self) -> None:
        res = {"regular.log": 10, "errors.log": 40}
        self.assertTrue(
            all(
                [
                    h.level == res[os.path.basename(h.baseFilename)]  # type: ignore
                    for h in self.py4ai_logger.handlers
                ]
            )
        )

    @logTest
    def test_file_logger_info_message(self) -> None:
        msg = "Example of logging with py4ai logger!"
        self.py4ai_logger.info(msg)
        self.py4ai_logger.handlers[0].flush()
        with open(self.py4ai_logger.handlers[0].baseFilename, "r") as fil:  # type: ignore
            lines = fil.readlines()
        lin = lines[-1]
        self.assertEqual(lin.split(" - ")[-1], f"{msg}\n")
        self.assertEqual(lin.split(" - ")[-2], "INFO")

    @logTest
    def test_file_logger_warning_message(self) -> None:
        warning_msg = "Example of logging a warning with py4ai logger!"
        self.py4ai_logger.warning(warning_msg)
        self.py4ai_logger.handlers[0].flush()
        with open(self.py4ai_logger.handlers[0].baseFilename, "r") as fil:  # type: ignore
            lines = fil.readlines()
        lin = lines[-1]
        self.assertEqual(lin.split(" - ")[-1], f"{warning_msg}\n")
        self.assertEqual(lin.split(" - ")[-2], "WARNING")

    @logTest
    def test_file_logger_error_message(self) -> None:
        error_msg = "Example of logging an error with py4ai logger!"
        self.py4ai_logger.error(error_msg)
        self.py4ai_logger.handlers[1].flush()
        with open(self.py4ai_logger.handlers[1].baseFilename, "r") as fil:  # type: ignore
            lines = fil.readlines()
        lin = lines[-1]
        self.assertEqual(lin.split(" - ")[-1], f"{error_msg}\n")
        self.assertEqual(lin.split(" - ")[-2], "ERROR")

    # TODO: [ND] Find a way to test except_logger: I know it works fine but I cannot find a way to raise exceptions
    #  without stopping the execution (and failing the test)
    # @logTest
    # def test_file_logger_catch_exceptions(self) -> None:
    #     except_logger = logger(name="except")
    #
    #     raise TypeError('Tipo Sbagliato')
    #
    #     with open(except_logger.handlers[1].baseFilename, 'r') as fil:
    #         lines = fil.readlines()
    #     lin = lines[-4:]
    #     self.assertEqual(lin[0].split(" - ")[-2], 'ERROR')
    #     self.assertEqual(lin[0].split(" - ")[-1], 'TypeError: Tipo Sbagliato\n')
    #     self.assertEqual(lin[-1], 'TypeError: Tipo Sbagliato\n')


if __name__ == "__main__":
    unittest.main()
    unset_TMP_FOLDER()
    clean_tmp_folder()
