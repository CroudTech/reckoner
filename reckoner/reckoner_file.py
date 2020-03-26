from .yaml.handler import Handler

class ReckonerFile(object):
  def __init__(self, namespace, repositories, helm_version, version):
    self._dict = {
      'namespace': namespace,
      'repositories': {}, 
      'minimum_versions': {
        'helm': helm_version,
        'reckoner': version
      },
      'helm_args': [],
      'charts': {},
    }
    self.repositories = repositories
    self._handler = Handler()

  def __getattr__(self, key):
        return self._dict.get(key)

  def __str__(self):
      return self._handler.dump(self._dict)

  def add_chart(self, 
    repo,
    chart,
    chart_version,
    release
  ):
    self._dict['charts'][release.name] = {
      'chart': chart,
      'repository': repo,
      'version': chart_version,
      'files': release.values_files
    }
    self._dict['repositories'][repo] = self.repositories[repo]