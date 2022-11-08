import os
import unittest

from py4ai.core.config import (
    Configuration,
    get_confs_in_path,
    load_from_file,
    merge_confs,
)
from py4ai.core.config.configurations import (
    AuthConfig,
    AuthenticationServiceConfig,
    BaseConfig,
    FileSystemConfig,
    LoggingConfig,
    MongoConfig,
)
from py4ai.core.logging import getDefaultLogger
from py4ai.core.tests.core import TestCase, logTest
from tests import DATA_FOLDER

os.environ["USER"] = os.environ.get("USER", "py4ai")
TEST_DATA_PATH = DATA_FOLDER
logger = getDefaultLogger()


class TempConfig(BaseConfig):
    @property
    def logging(self):
        return LoggingConfig(self.sublevel("logging"))

    @property
    def fs(self):
        return FileSystemConfig(self.sublevel("fs"))

    @property
    def auth(self):
        return AuthConfig(self.sublevel("auth"))

    @property
    def authentication(self):
        return AuthenticationServiceConfig(self.sublevel("authentication"))

    @property
    def mongo(self):
        return MongoConfig(self.sublevel("mongo"))


test_file = "defaults.yml"
os.environ["CONFIG_FILE"] = os.path.join(TEST_DATA_PATH, test_file)
conf_file = os.path.join(DATA_FOLDER, "specific.yml")
os.environ["LOGS_PATH"] = "logs"
os.environ["TEST_USER_VAR"] = "py4ai"


root = os.path.join("this", "is", "a", "folder")
credentials = os.path.join(root, "myfolder", "credentials.p")

config = TempConfig(
    BaseConfig(load_from_file(os.path.join(DATA_FOLDER, test_file))).sublevel("test")
)


class TestLoggingConfig(TestCase):
    @logTest
    def test_level(self):
        logger.info(f"Logging: {config.logging.level}")
        self.assertEqual(config.logging.level, "DEBUG")

    @logTest
    def test_filename(self):
        self.assertEqual(config.logging.filename, os.path.join("logs", "tests.log"))

    @logTest
    def test_default_config_file(self):
        self.assertEqual(
            config.logging.default_config_file,
            os.path.join("confs", "logConfDefaults.yaml"),
        )

    @logTest
    def test_capture_warnings(self):
        self.assertTrue(config.logging.capture_warnings)


class TestBaseConfig(TestCase):
    @logTest
    def test_sublevel(self):
        self.assertEqual(
            config.sublevel("fs").to_dict(),
            {
                "root": root,
                "folders": {"python": "myfolder"},
                "files": {"credentials": credentials},
            },
        )

    @logTest
    def test_getValue(self):
        self.assertEqual(config.getValue("fs")["root"], root)
        self.assertRaises(KeyError, config.getValue, "folders")

    @logTest
    def test_safeGetValue(self):
        self.assertEqual(config.safeGetValue("fs")["root"], root)
        self.assertIsNone(config.safeGetValue("folders"))

    @logTest
    def test_update_dict(self):
        new_config = config.update({"test": {"fs": {"root": "new_folder"}}})

        self.assertEqual(new_config.getValue("test")["fs"]["root"], "new_folder")
        self.assertEqual(
            new_config.config.meta["updated_params"],
            {"test": {"fs": {"root": "new_folder"}}},
        )

    @logTest
    def test_update_conf(self):
        new_config = config.update(
            Configuration(
                cfg_dict={"test": {"fs": {"root": "new_folder"}}},
                meta={"parse_datetime": None, "filepath": TEST_DATA_PATH},
            )
        )

        self.assertEqual(new_config.getValue("test")["fs"]["root"], "new_folder")
        self.assertEqual(
            new_config.config.meta["updated_params"],
            {"test": {"fs": {"root": "new_folder"}}},
        )
        self.assertEqual(
            new_config.config.meta["filepath"],
            TEST_DATA_PATH,
        )
        self.assertIsNone(new_config.config.meta["parse_datetime"])


class TestFileSystemConfig(TestCase):
    @logTest
    def test_root(self):
        self.assertEqual(config.fs.root, root)

    @logTest
    def test_getFolder(self):
        self.assertEqual(config.fs.getFolder("python"), "myfolder")

    @logTest
    def test_getFile(self):
        logger.info(f"Get File: {config.fs.getFile('credentials')}")
        self.assertEqual(config.fs.getFile("credentials"), credentials)


class TestAuthConfig(TestCase):
    @logTest
    def test_method(self):
        self.assertEqual(config.auth.method, "file")

    @logTest
    def test_filename(self):
        self.assertEqual(config.auth.filename, credentials)

    @logTest
    def test_user(self):
        self.assertEqual(config.auth.user, "userID")

    @logTest
    def test_password(self):
        self.assertEqual(config.auth.password, "passwordID")


class TestAuthenticationServiceConfig(TestCase):
    @logTest
    def test_secured(self):
        self.assertTrue(config.authentication.secured, "passwordID")

    @logTest
    def test_ap_name(self):
        self.assertEqual(config.authentication.ap_name, "cb")

    @logTest
    def test_cors(self):
        self.assertEqual(config.authentication.cors, "http://0.0.0.0:10001")

    @logTest
    def test_jwt_free_endpoints(self):
        self.assertEqual(
            config.authentication.jwt_free_endpoints,
            [
                "/api/v1/health/",
                "/api/v1/auth/login",
                "/api/v1/apidocs",
                "/api/v1/swagger.json",
                "/api/v1/salesforce/",
                "/api/v1/openBanking/",
            ],
        )

    @logTest
    def test_auth_service(self):
        self.assertEqual(config.authentication.auth_service.url, "http://0.0.0.0:10005")
        self.assertEqual(
            config.authentication.auth_service.check, "/tokens/{tok}/check"
        )
        self.assertEqual(
            config.authentication.auth_service.decode, "/tokens/{tok}/decode"
        )

    @logTest
    def test_check_service(self):
        self.assertEqual(
            config.authentication.check_service.url, "http://0.0.0.0:10001"
        )
        self.assertEqual(
            config.authentication.check_service.login, "/authentication/login"
        )
        self.assertEqual(
            config.authentication.check_service.logout, "/authentication/logout"
        )


class TestMongoConfig(TestCase):
    @logTest
    def test_host(self):
        self.assertEqual(config.mongo.host, "0.0.0.0")

    @logTest
    def test_port(self):
        self.assertEqual(config.mongo.port, 202020)

    @logTest
    def test_db_name(self):
        self.assertEqual(config.mongo.db_name, "database")

    @logTest
    def test_getCollection(self):
        self.assertEqual(config.mongo.getCollection("coll_name"), "coll_name")

    @logTest
    def test_auth(self):
        self.assertEqual(config.mongo.auth.method, "file")
        self.assertEqual(
            config.mongo.auth.filename,
            os.path.join(root, "myfolder", "credentials.auth.p"),
        )
        self.assertEqual(config.mongo.auth.user, "mongo.auth.db_user")
        self.assertEqual(config.mongo.auth.password, "mongo.auth.db_psswd")

    @logTest
    def test_admin(self):
        self.assertEqual(config.mongo.admin.method, "file")
        self.assertEqual(
            config.mongo.admin.filename,
            os.path.join(root, "myfolder", "credentials.admin.p"),
        )
        self.assertEqual(config.mongo.admin.user, "mongo.admin.db_user")
        self.assertEqual(config.mongo.admin.password, "mongo.admin.db_psswd")

    @logTest
    def test_authSource(self):
        self.assertEqual(config.mongo.authSource, "source")


class TestFunctions(TestCase):
    maxDiff = None

    @logTest
    def test_environ_variable_resolver(self):
        cfg = load_from_file(conf_file)
        path = cfg["storage"]["fs"]["folders"]["logs"]
        self.assertEqual(path, os.environ["LOGS_PATH"])

    @logTest
    def test_missing_environ_variable(self):
        value = os.environ.pop("LOGS_PATH")
        with self.assertRaises(KeyError) as context:
            load_from_file(conf_file)
        os.environ["LOGS_PATH"] = value
        self.assertIn("LOGS_PATH", str(context.exception))

    @logTest
    def test_load_from_file(self):
        cfg = load_from_file(conf_file)
        to_check = {
            "storage": {"fs": {"folders": {"logs": "logs"}}},
            "log": {
                "level": "DEBUG",
                "filename": "logs/tests.log",
                "default_config_file": "logs/confs/logConfDefaults.yaml",
                "capture_warnings": True,
            },
        }

        self.assertIsInstance(cfg, Configuration)
        self.assertEqual(cfg.to_dict(), to_check)

    @logTest
    def test_get_confs_in_path(self):
        self.assertEqual(
            set(get_confs_in_path(DATA_FOLDER, filename="*.yml")),
            {
                os.path.join(DATA_FOLDER, "defaults.yml"),
                os.path.join(DATA_FOLDER, "specific.yml"),
                os.path.join(DATA_FOLDER, "logging.yml"),
            },
        )
        self.assertEqual(
            get_confs_in_path(DATA_FOLDER, filename="specific.*"),
            [os.path.join(DATA_FOLDER, "specific.yml")],
        )

    @logTest
    def test_merge_confs(self):
        confs = merge_confs(
            filenames=get_confs_in_path(DATA_FOLDER, filename="specific.*"),
            default=get_confs_in_path(DATA_FOLDER, filename="defaults.yml")[0],
        )
        to_check = {
            "test": {
                "auth": {
                    "filename": "this/is/a/folder/myfolder/credentials.p",
                    "method": "file",
                    "password": "passwordID",
                    "user": "userID",
                },
                "authentication": {
                    "ap_name": "cb",
                    "auth_service": {
                        "check": "/tokens/{tok}/check",
                        "decode": "/tokens/{tok}/decode",
                        "url": "http://0.0.0.0:10005",
                    },
                    "check_service": {
                        "login": "/authentication/login",
                        "logout": "/authentication/logout",
                        "url": "http://0.0.0.0:10001",
                    },
                    "cors": "http://0.0.0.0:10001",
                    "jwt_free_endpoints": [
                        "/api/v1/health/",
                        "/api/v1/auth/login",
                        "/api/v1/apidocs",
                        "/api/v1/swagger.json",
                        "/api/v1/salesforce/",
                        "/api/v1/openBanking/",
                    ],
                    "secured": True,
                },
                "fs": {
                    "files": {"credentials": "this/is/a/folder/myfolder/credentials.p"},
                    "folders": {"python": "myfolder"},
                    "root": "this/is/a/folder",
                },
                "logging": {
                    "capture_warnings": True,
                    "default_config_file": "confs/logConfDefaults.yaml",
                    "filename": "logs/tests.log",
                    "level": "DEBUG",
                },
                "mongo": {
                    "admin": {
                        "filename": "this/is/a/folder/myfolder/credentials.admin.p",
                        "method": "file",
                        "password": "mongo.admin.db_psswd",
                        "user": "mongo.admin.db_user",
                    },
                    "auth": {
                        "filename": "this/is/a/folder/myfolder/credentials.auth.p",
                        "method": "file",
                        "password": "mongo.auth.db_psswd",
                        "user": "mongo.auth.db_user",
                    },
                    "authSource": "source",
                    "collections": {"coll_name": "coll_name"},
                    "db_name": "database",
                    "host": "0.0.0.0",
                    "port": 202020,
                },
                "user": "py4ai",
            },
            "log": {
                "capture_warnings": True,
                "default_config_file": "logs/confs/logConfDefaults.yaml",
                "filename": "logs/tests.log",
                "level": "DEBUG",
            },
            "storage": {"fs": {"folders": {"logs": "logs"}}},
        }
        self.assertEqual(confs.to_dict(), to_check)


if __name__ == "__main__":
    unittest.main()
