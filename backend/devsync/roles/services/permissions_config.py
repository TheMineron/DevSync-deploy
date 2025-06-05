import json
import logging
from pathlib import Path
from types import MappingProxyType
from typing import Annotated, Optional

from pydantic import BaseModel, ValidationError
from pydantic.fields import Field

from config import settings


logger = logging.getLogger('django')


class PermissionData(BaseModel):
    name: Annotated[str, Field(max_length=100)]
    category: Annotated[str, Field(max_length=100)]
    description: Annotated[str, Field(max_length=1256)]
    default: bool


class PermissionsConfig:
    """
    Stores metadata for all role permissions (name, category, description)
    """
    _permissions_meta: dict[str, PermissionData] = {}
    _loaded = False
    _permissions_json_filepath = Path(settings.STATIC_ROOT) / 'roles/permissions.json'

    @classmethod
    def get_permissions_meta(cls) -> MappingProxyType[str, PermissionData]:
        if not cls._loaded:
            cls._load_permissions_meta()
            cls._loaded = True
        return MappingProxyType(cls._permissions_meta)

    @classmethod
    def _load_permissions_meta(cls) -> None:
        with open(cls._permissions_json_filepath, 'r') as file:
            try:
                json_data = json.load(file)
                for key, value in json_data.items():
                    cls._permissions_meta[key] = PermissionData(**value)
            except (json.JSONDecodeError, ValidationError) as e:
                logger.critical(f"Permissions data could not be loaded: {str(e)}")
                raise

    @classmethod
    def get_permission_meta(cls, codename: str) -> Optional[PermissionData]:
        """Return the metadata of a specific permission with the given codename"""
        return cls._permissions_meta.get(codename, None)
