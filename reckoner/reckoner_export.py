from .helm.client import get_helm_client
from .reckoner_file import ReckonerFile
from .release import Release
from .yaml.handler import Handler
import json
import logging
import os
import re

class ReckonerExport:
  def __init__(self, namespace, dest, ignore_repo, version):
    self.namespace = namespace
    self.dest = dest 
    self.helm = get_helm_client(helm_arguments=[])
    self.yaml_handler = Handler()
    self.ignore_repo = ignore_repo
    self.version = version
    self.chart_repositories = {}
    self.repositories = self.get_repositories()
    pass

  @property
  def export_file(self):
    return "%s/%s/%s.yaml" % (self.dest, 'reckoner_files', self.namespace)

  def get_repositories(self):
    repositories = {}
    for repo in self.get_cli_table(self.helm.execute('repo', arguments=["list"]).stdout):
      repositories[repo['name']] = {
        'url': repo['url']
      }
    return repositories
    

  def get_releases(self):
    release_instances = []
    releases = self.helm.execute('list', arguments=["--namespace=%s" % self.namespace, "--output=json"])
    release_objects = json.loads(releases.stdout)
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    for release in release_objects['Releases']:
      release_arguments = {}
      for key, value in release.items():
        arg_name = pattern.sub('_', key).lower()
        release_arguments[arg_name] = value
      release_arguments['helm_client'] = self.helm
      release_instances.append(Release(**release_arguments))
    return release_instances

  def export(self):
    releases = self.get_releases()
    reckoner_file = ReckonerFile(
      namespace = self.namespace,
      repositories = self.repositories,
      helm_version = self.helm.version,
      version = self.version
    )
    
    for release in releases:
      self.set_values_files(release)
      reckoner_file.add_chart(
        repo = self.get_repository_for_release(release), 
        chart = self.get_chart(release), 
        chart_version = self.get_chart_version(release), 
        release = release,
      )
    reckoner_files_dest = os.path.dirname(self.export_file)
    os.makedirs(reckoner_files_dest, exist_ok=True)
    reckoner_file_ref = open(self.export_file, "w+")
    n = reckoner_file_ref.write(str(reckoner_file))
    reckoner_file_ref.close()
    return self.export_file
  
  def get_repository_for_release(self, release):
    if release.chart in self.chart_repositories:
      return self.chart_repositories[release.chart]
    result = self.helm.execute('search', arguments=[self.get_chart(release), '--version=%s' % self.get_chart_version(release)])
    found = self.get_cli_table(result.stdout)
    for item in found:
      repo = item['name'].split('/')[0]
      if re.search(r'stable', repo) and repo not in self.ignore_repo:
        self.chart_repositories[release.chart] = repo
        return repo
    return False

  def get_cli_table(self, table_string):
    table_rows = table_string.splitlines()
    header = [x.lower().strip().replace(' ', '_') for x in re.split('\t', table_rows.pop(0))]
    converted_rows = []
    for row in table_rows:
      row_items = re.split('\t', row)
      converted_row = { val : row_items[i].strip() for i, val in enumerate(header) }
      converted_rows.append(converted_row)
    return converted_rows
    

  def set_values_files(self, release):
    path = self.namespace.split('-', 2) + [self.get_chart(release)]
    values_path = "/".join([self.dest, *path])
    os.makedirs(values_path, exist_ok=True)
    values = self.helm.execute('get', arguments=['values', release.name])
    values_filename = "%s/%s.yaml" % (values_path, release.name)
    values_file = open(values_filename, "w+")
    n = values_file.write(values.stdout)
    values_file.close()
    logging.info("Created values file %s" % values_filename)
    release.set_values_file(values_filename)

  def get_chart(self, release):
    pattern = re.compile(r'\-([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+)?$')
    return pattern.sub('', release.chart)
  
  def get_chart_version(self, release):
    pattern = re.compile(r'(([0-9]+)\.([0-9]+)\.([0-9]+))')
    return pattern.search(release.chart).group(1)

  def get_repo(self, release):
    chart = self.get_chart(release)

