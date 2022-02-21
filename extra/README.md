# Extra python scripts

* `dump3d.py` replicates _exactly_ the functionality of the survex
  `dump3d` command in pure python, for debugging.

* `test3d.py` was used for debugging the treatment of the passage wall
  data.  It runs like `dump3d.py`, but additionally generates a number of
  `*.dat` files containing xy data which can be read into a standard
  plotting package.

* `old3d2json.py` converts old-style ASCII .3d files at v0.01 to
  GeoJSON, writing to stdout, and optionally adding a CRS.

Copyright &copy; (2018-2022) Patrick B Warren.
