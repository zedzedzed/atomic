Python script to construct a working installation of WordPress, together with plugins and themes regardless of using Git or Subversion. Atomic acts similar to SVN:Externals and Composer.

Although it was designed to config manage the installation of WordPress, plugins and themes across different environments, Atomic can be used for non WordPress purposes where you have an installation directory that consists of many folders of repositories.

Requires
--
* Python3+
* git
* svn

Folder structure
--
If you use the supplied _specfication.json.template file as a guide, the resulting folder structure will be

/current-working-directory/
* /core/
* /wp-contents/plugins/akismet/
* /wp-contents/plugins/table-of-contents-plus/
* /wp-contents/plugins/wordpress-importer/
* /wp-contents/themes/twentyseventeen/

Config
--
The first step is to copy **_specification.json.template** file to **_specification.json** and amend it to include the right version of WordPress, and the components that you need. You should place the file into the destination installation directory, eg: /opt/www/wordpress/

Usage
--
On developer instances, tell Git to cache your Git credentials in memory so it doesn't prompt you for each matching repository.
```
$ git config --global credential.helper cache
```

View usage guide:
```
$ _atomic.py -h
usage: _atomic.py [-h] [--spec SPEC] [--core] [-c COM]

optional arguments:
  -h, --help            show this help message and exit
  --spec SPEC, --specification SPEC, --conf SPEC, --config SPEC
                        Location of the specification json file. Defaults to
                        _specification.json in the current directory.
  --core                Synchronises WordPress core
  -c COM, --com COM, --component COM
                        Name of component to synchronise
```

If you run without any parameters, it will do everything in _specification.json.

Do core only:
```
$ _atomic.py --core
```

Do the akismet and wordpress importer plugins, and the twentyseventeen theme. These are all components.
```
$ _atomic.py --com akismet --com wordpress-importer --com twentyseventeen
```

Atomic does not need to exist in the current directory.
```
/my/current/directory/$ /path/to/_atomic.py
```
The above will load _specification.json in **/my/current/directory/**

The _specification.json file does not need to be in the current directory either.
```
/my/current/directory/$ /path/to/_atomic.py --spec /opt/www/wordpress/_specification.json
```
