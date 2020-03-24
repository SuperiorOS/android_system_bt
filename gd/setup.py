#!/usr/bin/env python3
#
#   Copyright 2020 - The Android Open Source Project
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from distutils import log
import os
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
import stat
import subprocess
import sys

install_requires = [
    'grpcio',
]

host_executables = [
    'root-canal',
    'bluetooth_stack_with_facade',
]


def setup_acts_for_cmd_or_die(cmd_str):
    acts_framework_dir = os.path.abspath('acts_framework')
    acts_setup_bin = os.path.join(acts_framework_dir, 'setup.py')
    cmd = [sys.executable, acts_setup_bin, cmd_str]
    subprocess.check_call(cmd, cwd=acts_framework_dir)


def set_permssions_for_host_executables(outputs):
    for file in outputs:
        if os.path.basename(file) in host_executables:
            current_mode = os.stat(file).st_mode
            new_mode = current_mode | stat.S_IEXEC
            os.chmod(file, new_mode)
            log.log(
                log.INFO, "Changed file mode of %s from %s to %s" %
                (file, oct(current_mode), oct(new_mode)))


class InstallLocalPackagesForInstallation(install):

    def run(self):
        self.announce('Installing ACTS for installation', log.INFO)
        setup_acts_for_cmd_or_die("install")
        self.announce('ACTS installed for installation.', log.INFO)
        install.run(self)
        set_permssions_for_host_executables(self.get_outputs())


class InstallLocalPackagesForDevelopment(develop):

    def run(self):
        log.log(log.INFO, 'Installing ACTS for development')
        setup_acts_for_cmd_or_die("develop")
        log.log(log.INFO, 'ACTS installed for development')
        develop.run(self)
        set_permssions_for_host_executables(self.get_outputs())


def main():
    # Relative path from calling directory to this file
    our_dir = os.path.dirname(__file__)
    # Must cd into this dir for package resolution to work
    # This won't affect the calling shell
    os.chdir(our_dir)
    setup(
        name='bluetooth_cert_tests',
        version='1.0',
        author='Android Open Source Project',
        license='Apache2.0',
        description="""Bluetooth Cert Tests Package""",
        # Include root package so that bluetooth_packets_python3.so can be
        # included as well
        packages=[''] + find_packages(exclude='acts_framework'),
        install_requires=install_requires,
        package_data={
            '': host_executables + ['*.so', 'lib64/*.so', 'target/*'],
            'cert': ['all_test_cases'],
        },
        cmdclass={
            'install': InstallLocalPackagesForInstallation,
            'develop': InstallLocalPackagesForDevelopment,
        })


if __name__ == '__main__':
    main()
