
# -- coding: utf-8 --

# Copyright 2017 Reactive Ops Inc.
#
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.__init__.py

import unittest

import coloredlogs
import logging
import os
import git
import subprocess
import shutil
import mock
import autohelm

from autohelm.autohelm import AutoHelm
from autohelm.config import Config
from autohelm.course import Course
from autohelm.repository import Repository
from autohelm.exception import MinimumVersionException, AutoHelmCommandException
from autohelm import Response
from autohelm.helm import Helm


# Test properties of the mock
@mock.patch('autohelm.autohelm.Config', autospec=True)
@mock.patch('autohelm.autohelm.Course', autospec=True)
@mock.patch.object(Helm, 'server_version')
class TestAutoHelmAttributes(unittest.TestCase):
    name = "test-autohelm-attributes"

    def test_config(self, *args):
        autohelm_instance = autohelm.autohelm.AutoHelm()
        self.assertTrue(hasattr(autohelm_instance, 'config'))

    def test_course(self, *args):
        autohelm_instance = autohelm.autohelm.AutoHelm()
        self.assertTrue(hasattr(autohelm_instance, 'course'))

    def test_helm(self, *args):
        autohelm_instance = autohelm.autohelm.AutoHelm()
        self.assertTrue(hasattr(autohelm_instance, 'helm'))


# Test methods
@mock.patch('autohelm.autohelm.Config', autospec=True)
@mock.patch('autohelm.autohelm.Course', autospec=True)
@mock.patch.object(Helm, 'server_version')
class TestAutoHelmMethods(unittest.TestCase):
    name = 'test-autohelm-methods'

    def test_install_succeeds(self, *args):
        autohelm_instance = autohelm.autohelm.AutoHelm()
        autohelm_instance.course.plot.return_value = True
        install_response = autohelm_instance.install()
        self.assertIsInstance(install_response, bool)
        self.assertTrue(install_response)

test_course = "./tests/test_course.yml"
git_repo_path = "./test"

test_release_names = ['cluster-autoscaler', 'spotify-docker-gc', 'centrifugo', 'spotify-docker-gc-again']
test_repositories = ['stable', 'incubator'],
test_minimum_versions = ['helm', 'autohelm']
test_repository_dict = {'name': 'test_repo', 'url': 'https://kubernetes-charts.storage.googleapis.com'}
test_autohelm_version = "1.0.0"

test_release_name = 'spotify-docker-gc-again'
test_chart_name = 'spotify-docker-gc'

test_git_repository_chart = 'centrifugo'
test_git_repository = {'path': 'stable', 'git': 'https://github.com/kubernetes/charts.git'}
test_incubator_repository_chart = 'cluster-autoscaler'
test_incubator_repository_str = 'stable'

test_flat_values_chart = 'cluster-autoscaler'
test_flat_values = {
    'string': 'string',
    'integer': 10,
    'boolean': True,
}


test_nested_values_chart = 'centrifugo'
test_nested_values = {
    'even':
    [
        'in',
        'a',
        'list',
        {
            'or':
            {
                'dictionary':
                {
                    'int': 999,
                    'of':
                    'items'
                }
            }
        }
    ],
    'nested':
    {
        'values':
        {
            'are': 'supported'
        }
    }
}

test_values_strings_chart = "spotify-docker-gc"

test_default_files_path = "~/.helm"
test_files_path = 'test_files/.helm'
test_archive_pathlet = 'cache/archive'
test_helm_archive = "{}/{}".format(test_files_path, test_archive_pathlet)

test_helm_args = ['helm', 'version', '--client']
test_helm_version_return_string = '''Client: &version.Version{SemVer:"v2.11.0", GitCommit:"2e55dbe1fdb5fdb96b75ff144a339489417b146b", GitTreeState:"clean"}'''
test_helm_version = '2.11.0'

test_helm_repo_return_string = '''NAME          URL
stable      https://kubernetes-charts.storage.googleapis.com
local       http://127.0.0.1:8879/charts
incubator   https://kubernetes-charts-incubator.storage.googleapis.com'''
test_helm_repo_args = ['helm', 'repo', 'list']
test_helm_repos = [Repository({'url': 'https://kubernetes-charts.storage.googleapis.com', 'name': 'stable'}), Repository({'url': 'http://127.0.0.1:8879/charts', 'name': 'local'})]

test_tiller_present_return_string = '''NAME         REVISION    UPDATED                     STATUS      CHART               APP VERSION NAMESPACE
centrifugo  1           Tue Oct  2 16:19:01 2018    DEPLOYED    centrifugo-2.0.1    1.7.3       test'''
test_tiller_present_args = ['helm', 'list']

test_tiller_not_present_return_string = ''
test_tiller_not_present_args = ['helm', 'list']

test_repo_update_return_string = '''Hang tight while we grab the latest from your chart repositories...
...Skip local chart repository
...Successfully got an update from the "incubator" chart repository
...Successfully got an update from the "stable" chart repository
Update Complete. ⎈ Happy Helming!⎈'''
test_repo_update_args = ['helm', 'repo', 'update']


test_repo_install_args = ['helm', 'repo', 'add', 'test_repo', 'https://kubernetes-charts.storage.googleapis.com']
test_repo_install_return_string = '"test_repo" has been added to your repositories'


def setUpModule():
    coloredlogs.install(level="DEBUG")
    config = Config()
    config.local_development = True

    os.makedirs(test_helm_archive)
    os.environ['HELM_HOME'] = test_files_path

    # This will eventually be need for integration testing
    # args = ['helm','init','-c','--home', "{}/.helm".format(test_files_path)]
    # subprocess.check_output(args)


def tearDownModule():
    shutil.rmtree(test_files_path)


class TestBase(unittest.TestCase):

    def setUp(self):
        self.subprocess_mock_patch = mock.patch('subprocess.Popen')
        self.subprocess_mock = self.subprocess_mock_patch.start()
        self.m = mock.Mock()

    def configure_subprocess_mock(self, stdout, stderr, returncode):
        attrs = {'returncode': returncode, 'communicate.return_value': (stdout, stderr)}
        self.m.configure_mock(**attrs)
        self.subprocess_mock.return_value = self.m

    def tearDown(self):
        self.subprocess_mock_patch.stop()


class TestAutoHelm(TestBase):
    name = "test-pentagon-base"

    def setUp(self):
        super(type(self), self).setUp()
        # This will eventually be need for integration testing
        # repo = git.Repo.init(git_repo_path)
        # os.chdir(git_repo_path)
        # subprocess.call(["helm", "create", "chart"])
        # # Create git chart in a git repo, then have it checkout the repo from that location
        # logging.debug(os.listdir("./"))
        # os.chdir("../")
        self.configure_subprocess_mock(test_tiller_present_return_string, '', 0)
        with open(test_course) as f:
            self.a = AutoHelm(file=f, local_development=True)

    # def tearDown(self):
    #     self.a = None
    #     subprocess.call(['rm', '-rf', git_repo_path])

    def test_instance(self):
        self.assertIsInstance(self.a, AutoHelm)

    def test_config_instance(self):
        self.assertIsInstance(self.a.config, Config)

    def test_install(self):
        self.assertTrue(self.a.install())


class TestCourse(TestBase):

    def setUp(self):
        super(type(self), self).setUp()
        self.configure_subprocess_mock(test_repo_update_return_string, '', 0)
        with open(test_course) as f:
            self.c = Course(f)

        self.test_repository = Repository(test_repository_dict)

    def test_config_instance(self):
        self.assertIsInstance(self.c.config, Config)

    def test_course_values(self):
        self.assertIsInstance(self.c, Course)
        self.assertEqual([chart._release_name for chart in self.c.charts], test_release_names)
        self.assertNotEqual([chart.name for chart in self.c.charts], test_release_names)
        self.assertEqual(self.c.repositories[0].name, test_repository_dict['name'])
        self.assertEqual(self.c.repositories[0].url,  test_repository_dict['url'])
        self.assertEqual(self.c.minimum_versions.keys(), test_minimum_versions)
        self.assertIsInstance(self.c.repositories, list)

    def test_minimum_version(self):
        self.configure_subprocess_mock(test_helm_version_return_string, '', 0)
        self.c.minimum_versions['autohelm'] = test_autohelm_version
        self.assertRaises(MinimumVersionException, self.c._compare_required_versions)

    def test_plot_course(self):
        self.configure_subprocess_mock('', '', 0)  # Lots more work do do here with the installation of the list of charts
        self.c.plot(list(self.c._dict['charts']))
        self.assertEqual(self.c._charts_to_install, self.c.charts)


class TestChart(TestBase):

    def setUp(self):
        super(type(self), self).setUp()
        self.configure_subprocess_mock(test_tiller_present_return_string, '', 0)
        with open(test_course) as f:
            self.a = AutoHelm(file=f, local_development=True)
        self.charts = self.a.course.charts

    def test_releasename_is_different_than_chart_name(self):
        for chart in self.charts:
            if chart == test_release_name:
                self.assertNotEqual(chart._release_name, chart.name)
                self.assertEqual(chart.name, test_chart_name)

    def test_chart_repositories(self):
        for chart in self.charts:
            self.assertIsNotNone(chart.repository)
            self.assertIsInstance(chart.repository, Repository)
            if chart.name == test_git_repository_chart:
                self.assertEqual(chart.repository.git, Repository(test_git_repository).git)
                self.assertEqual(chart.repository.path, Repository(test_git_repository).path)
            elif chart.name == test_incubator_repository_chart:
                self.assertEqual(chart.repository.name, Repository(test_incubator_repository_str).name)
                self.assertIsNone(chart.repository.url)

    def test_chart_values(self):
        for chart in self.charts:
            if chart.name == test_flat_values_chart:
                self.assertEqual(chart.values, test_flat_values)
                self.assertIsInstance(chart.values, dict)
                self.assertIsInstance(chart.values['string'], str)
                self.assertIsInstance(chart.values['integer'], int)
                self.assertIsInstance(chart.values['boolean'], bool)
            elif chart.name == test_nested_values_chart:
                self.assertEqual(chart.values, test_nested_values)
            elif chart.release_name == test_values_strings_chart:
                self.assertEqual(chart.values_strings, test_flat_values,)
                self.assertIsInstance(chart.values_strings['string'], str)
                self.assertIsInstance(chart.values_strings['integer'], int)
                self.assertIsInstance(chart.values_strings['boolean'], bool)

    def test_debug_args(self):
        chart = self.charts[0]

        chart.config.debug = True
        self.assertEqual(chart.debug_args, ['--debug'])

        chart.config.debug = False
        chart.config.dryrun = True
        self.assertEqual(chart.debug_args, ['--dry-run', '--debug'])

    # FIXME: Related to the FIXME in install() of Chart class.
    @unittest.skip("Skipping non-implmeneted test.")
    def test_chart_at_git_root(self):
        """
        Chart should support cloning git repositories where the chart is in
        the root of the repository.
        """
        pass


class TestRepository(TestBase):

    def test_git_repository(self):
        self.configure_subprocess_mock('', '', 0)
        r = Repository(test_git_repository)
        self.assertIsInstance(r, Repository)
        self.assertEqual(r.git, test_git_repository['git'])
        self.assertEqual(r.path, test_git_repository['path'])
        self.assertEqual(r.install(), None)

    def test_tgz_repository(self):
        self.configure_subprocess_mock('', '', 0)
        r = Repository(test_repository_dict)
        self.assertIsInstance(r, Repository)
        self.assertEqual(r.name, test_repository_dict['name'])
        self.assertEqual(r.url, test_repository_dict['url'])
        self.assertEqual(r.install(), Response('', '', 0))


class TestConfig(TestBase):

    def setUp(self):
        super(type(self), self).setUp()
        self.c1 = Config()
        self.c2 = Config()

    def test_home_with_envvar_set(self):
        self.assertEqual(self.c1.home, test_files_path)
        self.assertEqual(self.c1.archive, '{}/{}'.format(test_files_path, test_archive_pathlet))

    def test_borg_pattern(self):
        self.assertEqual(self.c1.__dict__, self.c2.__dict__)
        self.c1.test = 'value'
        self.assertEqual(self.c1.__dict__, self.c2.__dict__)


class TestHelm(TestBase):

    def setUp(self):
        super(type(self), self).setUp()
        self.helm = Helm()

    def test_helm_version(self):
        self.configure_subprocess_mock(test_helm_version_return_string, '', 0)
        self.assertEqual(self.helm.client_version, test_helm_version)
        self.subprocess_mock.assert_called_once_with(test_helm_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_installed_repositoried(self):
        self.configure_subprocess_mock(test_helm_repo_return_string, '', 0)
        self.assertEqual(self.helm.repositories, test_helm_repos)
        self.subprocess_mock.assert_called_once_with(test_helm_repo_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
