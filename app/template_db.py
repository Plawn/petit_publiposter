import json
import os

from typing import Dict

import minio

from .template_engine.ReplacerMiddleware import (FuncReplacer,
                                                 MultiReplacer)
from .template_engine import template_engines
from .minio_creds import MinioCreds, MinioPath
from .templator import Templator
from datetime import timedelta
import subprocess

OUTPUT_DIRECTORY_TOKEN = 'output_bucket'

# placeholder for now
BASE_REPLACER = MultiReplacer([FuncReplacer])


class TemplateDB:
    """Holds everything to publipost all types of templates
    """

    def __init__(self, manifest: dict, engine_settings: dict, time_delta: timedelta, temp_folder: str, minio_creds: MinioCreds):
        self.minio_creds = minio_creds
        self.minio_instance = minio.Minio(
            self.minio_creds.host, self.minio_creds.key, self.minio_creds.password)
        self.manifest: Dict[str, Dict[str, str]] = manifest
        self.temp_folder = temp_folder
        self.templators: Dict[str, Templator] = {}
        self.time_delta = time_delta
        self.engine_settings = engine_settings
        self.init()

    def init(self):
        self.__init_template_servers()
        self.__init_templators()
        for templator in self.templators.values():
            templator.pull_templates()

    def render_template(self, _type: str, name: str, data: Dict[str, str],  output: str):
        return self.templators[_type].render(name, data, output)

    def __init_template_servers(self) -> None:
        for name in template_engines:
            for command in self.engine_settings[name]:
                subprocess.call(command, shell=True)

    def __init_templators(self):
        for bucket_name, settings in self.manifest.items():
            try:
                self.templators[settings['type']] = Templator(
                    self.minio_instance,
                    self.temp_folder,
                    MinioPath(bucket_name),
                    MinioPath(settings[OUTPUT_DIRECTORY_TOKEN]),
                    self.time_delta,
                    BASE_REPLACER
                )
            except Exception as e:
                print(e)

    def to_json(self):
        return {
            name: templator.to_json() for name, templator in self.templators.items()
        }
