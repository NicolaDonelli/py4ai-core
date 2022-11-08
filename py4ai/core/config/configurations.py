"""Configuration classes."""
from datetime import datetime
from typing import Any, Hashable, List, Union

import pytz
from cfg_load import Configuration

from py4ai.core.types import PathLike
from py4ai.core.utils.dict import union


class BaseConfig(object):
    """Base configuration class."""

    def __init__(self, config: Configuration):
        """
        Class instance initializer.

        :param config: configuration
        """
        self.config = config

    def sublevel(self, name: Hashable) -> Configuration:
        """
        Return a sublevel of the main configuration.

        :param name: name of the sublevel
        :return: configuration of the sublevel
        """
        return Configuration(
            self.config[name], self.config.meta, self.config.meta["load_remote"]
        )

    def getValue(self, name: Hashable) -> Any:
        """
        Get the value of a configuration node.

        :param name: name of the configuration node
        :return: value of the configuratio node
        """
        return self.config[name]

    def safeGetValue(self, name: Hashable) -> Any:
        """
        Get the value of a configuration node, gracefully returning None if the node does not exist.

        :param name: name of the node
        :return: value of the node, or None if the node does not exist
        """
        return self.config.get(name, None)

    def update(self, other: Union[dict, Configuration]) -> "BaseConfig":
        """
        Update the current configuration.

        :param other: dictionary or Configuration containing the nodes of the configuration to be updated.
            In case other is a Configuration also metadata will be updated to other's metadata.
        :return: new configuration with the updated nodes
        :raises ValueError: if other is not a dict or a Configuration
        """
        if isinstance(other, dict):
            config = Configuration(
                union(self.config.to_dict(), other),
                union(
                    self.config.meta,
                    {
                        "updated_params": other,
                        "modification_datetime": datetime.now().astimezone(
                            tz=pytz.timezone("Europe/Rome")
                        ),
                    },
                ),
                self.config.meta["load_remote"],
            )
            return type(self)(config)
        elif isinstance(other, Configuration):
            newconfig = self.config.update(other)
            return type(self)(
                Configuration(
                    newconfig.to_dict(),
                    union(
                        newconfig.meta,
                        {
                            "updated_params": other.to_dict(),
                            "modification_datetime": datetime.now().astimezone(
                                tz=pytz.timezone("Europe/Rome")
                            ),
                        },
                    ),
                )
            )
        else:
            raise ValueError(f"Type {type(other)} cannot be merged to Configuration")


class FileSystemConfig(BaseConfig):
    """Configuration for file system paths."""

    @property
    def root(self) -> PathLike:
        """
        Return the root node value.

        :return: root node value
        """
        return self.getValue("root")

    def getFolder(self, path: Hashable) -> PathLike:
        """
        Return the folder name.

        :param path: name of the configuration node
        :return: folder name
        """
        return self.config["folders"][path]

    def getFile(self, file: Hashable) -> PathLike:
        """
        Return the file name.

        :param file: name of the configuration node
        :return: file name
        """
        return self.config["files"][file]


class AuthConfig(BaseConfig):
    """Authetication configuration."""

    @property
    def method(self) -> str:
        """
        Return the authentication method.

        :return: authentication method
        """
        return self.getValue("method")

    @property
    def filename(self) -> PathLike:
        """
        Return the name of the file containing the authentication details.

        :return: name of the file containing the authentication details
        """
        return self.getValue("filename")

    @property
    def user(self) -> str:
        """
        Return the user name.

        :return: user name
        """
        return self.getValue("user")

    @property
    def password(self) -> str:
        """
        Return the password.

        :return: password
        """
        return self.getValue("password")


class AuthService(BaseConfig):
    """Configuration for the authentication data."""

    @property
    def url(self) -> str:
        """
        Return the url of the authentication service.

        :return: url of the authentication service
        """
        return self.getValue("url")

    @property
    def check(self) -> str:
        """
        Return check.

        :return: check
        """
        return self.getValue("check")

    @property
    def decode(self) -> str:
        """
        Return decode.

        :return: decode
        """
        return self.getValue("decode")


class CheckService(BaseConfig):
    """Configuration for the check service."""

    @property
    def url(self) -> str:
        """
        Return the url of the check service.

        :return: url of the check service.
        """
        return self.getValue("url")

    @property
    def login(self) -> str:
        """
        Return the login url.

        :return: login url
        """
        return self.getValue("login")

    @property
    def logout(self) -> str:
        """
        Return the logout url.

        :return: logout url
        """
        return self.getValue("logout")


class AuthenticationServiceConfig(BaseConfig):
    """Configuration of the authentication service."""

    @property
    def secured(self) -> bool:
        """
        Return the secured flag.

        :return: secured flag
        """
        return self.getValue("secured")

    @property
    def ap_name(self) -> str:
        """
        Return the ap name.

        :return: ap name
        """
        return self.getValue("ap_name")

    @property
    def jwt_free_endpoints(self) -> List[str]:
        """
        Return the jwt free endpoints.

        :return: jwt free endpoints
        """
        return self.getValue("jwt_free_endpoints")

    @property
    def auth_service(self) -> AuthService:
        """
        Return the authentication data.

        :return: authentication data
        """
        return AuthService(self.sublevel("auth_service"))

    @property
    def check_service(self) -> CheckService:
        """
        Return the check service configuration.

        :return: check service configuration
        """
        return CheckService(self.sublevel("check_service"))

    @property
    def cors(self) -> str:
        """
        Return the cors.

        :return: cors
        """
        return self.getValue("cors")


class LoggingConfig(BaseConfig):
    """Logging configuration."""

    @property
    def level(self) -> str:
        """
        Returnn logging level.

        :return: level
        """
        return self.getValue("level")

    @property
    def filename(self) -> PathLike:
        """
        Name of the file where logs are stored.

        :return: filename
        """
        return self.getValue("filename")

    @property
    def default_config_file(self) -> PathLike:
        """
        Return default logging configuration file.

        :return: default config file
        """
        return self.getValue("default_config_file")

    @property
    def capture_warnings(self) -> bool:
        """
        Flag that determines whether waring are captured.

        :return: capture warnings
        """
        return self.getValue("capture_warnings")


class MongoConfig(BaseConfig):
    """Configuration for a Mongo DB."""

    @property
    def host(self) -> str:
        """
        Return ost name.

        :return: host name
        """
        return self.getValue("host")

    @property
    def port(self) -> int:
        """
        Return port.

        :return: port
        """
        return self.getValue("port")

    @property
    def db_name(self) -> str:
        """
        Return database name.

        :return: database name
        """
        return self.getValue("db_name")

    def getCollection(self, name) -> str:
        """
        Return collection name at a given configuration node.

        :param name: configuration node name
        :return: collection name
        """
        return self.config["collections"][name]

    @property
    def auth(self) -> AuthConfig:
        """
        Return authetication config.

        :return: authetication config
        """
        return AuthConfig(self.sublevel("auth"))

    @property
    def admin(self) -> AuthConfig:
        """
        Return administrator authentication config.

        :return: administrator authentication config
        """
        return AuthConfig(self.sublevel("admin"))

    @property
    def authSource(self) -> Any:
        """
        Return the authentication source.

        :return: authentication source
        """
        return self.safeGetValue("authSource")
