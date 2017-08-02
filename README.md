Python script to construct a working installation of WordPress, together with plugins and themes. Atomic acts similar to SVN:Externals and Composer.

Requires
* Python3+
* git
* svn

On developer instances, tell Git to cache your Git credentials in memory so it doesn't prompt you for each matching repository.
```
$ git config --global credential.helper cache
```

View usage guide:
```
$ python3 _atomic.py -h
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

If you run without any paramters, it will do everything in _specification.json.

Do core only:
```
$ python3 _atomic.py --core
```

Do the 99 and gravityforms plugins, aofm and arpc themes. These are all components.
```
$ python3 _atomic.py --com 99 --com gravityforms --com aofm --com arpc
```

