# QGIS3 plugin to import survex .3d files

_UNFINISHED ... work in progress ... watch this space_

_Requires QGIS3 and 
.3d files produced by survex &ge; 1.2.14 for v8 binary format._

### Features

* no dependencies, natively reads binary v8 format survex .3d files ;
* import stations and legs with full metadata ;
* features carry _z_ dimension (elevation) data ;
* create passage walls, cross-sections, and polygons from LRUD data ;
* CRS can be set from PROJ.4 string embedded in .3d file ;
* save results into a GeoPackage (.gpkg) shapefile.

### Installation

To install the plugin:

* clone or download this repository ;
* copy the `survex_import` directory to where the QGIS3 python3 plugins
  should be installed (see below) ;
* run QGIS3 and enable the plugin by going to 'Plugins &rarr; Manage and
  Install Plugins...' and make sure the box next to 'Import .3d file'
  is checked, in the 'Installed' tab.

When installed, a menu item 'Import .3d file' should appear on the
'Vector' drop-down menu in the main QGIS3 window, and (possibly) a
.3d icon in a toolbar (if enabled).

Under unix (linux) the copy command would be
```
cp -R survex_import ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins
```

Note that the `SurvexImport` directory in the repository is
automatically populated by running `pb_tool deploy` in the
`..\survex_import` directory.  Make all edits in that directory; any
changes or additions made in `SurvexImport` will be overwritten!

### Usage

Selecting 'Import .3d file' (or clicking on the .3d icon) brings up a
window for the user to select a .3d file with a number of options:

* Import legs, with options to include splay, duplicate, and surface legs ;
* Import stations, with the option to include surface stations (\*) ;
* Import passage data computed from LRUDs, with the option to use clino weights (see below):
    - as polygons, with an option to include mean up / down data ;
    - as walls ;
    - as cross sections ;
    - as traverses, showing the centrelines used for above ;
* Get CRS from .3d file, or inherit from QGIS3 project ;
* Keep features from previous import(s) ;
* Select a GeoPackage (.gpkg) file to save results (optional).
  
(\*) In rare cases a station may be flagged both surface and
underground, in which case it is imported even if the 'surface' option
is left unchecked. 

On clicking OK, vector layers are created to contain the imported
features as desired.  Legs, walls, cross sections, and traverses are
imported as line strings in separate vector layers for convenience.
All created layers are saved to the GeoPackage file if requested (any
existing content is overwritten).

If 'keep features' is selected, then previously imported features are
not discarded, and the newly-created layers will contain both the
previously imported features plus any new features imported from the
designated .3d file.  This choice allows processed survey data sets to
be combined from multiple sources.  Note that cumulative imports do
not result in features being overwritten, even if they happen to share
the same name, since all features are assigned a unique ID.

#### Imported attributes

All layers are created with an ELEVATION attribute, for convenience.
For stations this is the just the _z_ dimension.  For all
other features it is the mean elevation.

For station and leg layers, the following additional attribute fields
that are created:

* stations: NAME, and flags SURFACE, UNDERGROUND, ENTRANCE, EXPORTED,
  FIXED, ANON

* legs: NAME, STYLE, DATE1, DATE2, NLEGS (\*), LENGTH (\*), ERROR (\*),
  ERROR_HORIZ (\*), ERROR_VERT (\*), and flags SURFACE, DUPLICATE, SPLAY

(\*) These fields correspond to the error data reported in the .3d
file, which is only generated (by survex) if loop closures are present.

The flags are integer fields set to 0 or 1.

The STYLE field for legs is one of NORMAL, DIVING, CARTESIAN,
CYLPOLAR, or NOSURVEY.

The DATE fields are either the same, or represent a date
range, in the standard QGIS3 format YYYY-MM-DD.

If up / down data for passage polygons is requested, then the polygons have
MEAN_UP and MEAN_DOWN attributes in addition to ELEVATION.  These are
computed from the LRUD data for the two stations at either end of the
leg.  They can be used in 3d work (see end).

For the most part importing the CRS from the .3d file should work as
expected if the survey data has been georeferenced using the survex
`*cs` and `*cs out` commands.  If it doesn't work, or this information
isn't present, one can instead inherit the CRS from the current QGIS3
project.  If neither of these options is selected, a CRS dialog box
may appear for each layer, or a default CRS will be chosen
automatically, depending on the system-wide QGIS3 settings.
To maximise the likelihood that CRS import from .3d file works as
expected, use an EPSG code in the `*cs out` survex command rather than
a PROJ.4 string.

[_The following may not apply to QGIS3?_]
There is one point to bear in mind regarding the _z_ dimension data.
Because of the (current) limitations for creating vector layers in
memory, the layer type does not explicitly
know that the features include _z_ dimensions.  To ensure the _z_
dimension data is correctly incorporated when saving layers by hand,
in the 'Save as ...'  dialog make sure that the geometry type is
specified (ie 'Point' for stations, 'Polygon' for polygons, and
'LineString' for everything else) and the 'Include _z_ dimension' box
is checked.  This is done automatically when saving to the GeoPackage
file if requested.

#### Passage walls

Passage walls (as line strings), polygons, and cross sections (as
lines) are computed from the left and right measurements in the LRUD
data in the same way that the `aven` viewer in survex displays passage
'tubes' (well, near enough...).  The direction of travel (bearing) is
worked out, and used to compute the positions of points on the left
and right hand passage walls.  These wall points are then assembled
into the desired features (walls, polygons, cross sections).

The direction of travel is inferred from the directions of the two
legs on either side of the given station (with special treatment for
stations at the start and end of a traverse).  In averaging these,
either the legs can be weighted equally (except true plumbs which
break the sequence), or the option is given to weight legs by the
cosine of the inclination (computed from the processed data, not the
actual clino reading).  The former is the default, and the latter
corresponds to checking the 'use clino weights' box in the import
dialog.  This alternative option downplays the significance of the
occasional steeply inclined leg in an otherwise horizontal passage.

One might want to do this for the following reason.  In the 'good old
days' steeply inclined legs were usually avoided as they are difficult
to sight a compass along, and instead good practice was to keep legs
mostly horizontal and add in the occasional plumbed leg when dealing
with rough ground.  Also pitches were nearly always plumbed.  This
meant that inferring passage direction as a simple average, ignoring
plumbed legs, was most likely correct.  For modern surveying with
digital instruments, this is no longer the case: there is no loss of
accuracy for steeply inclined legs, and shining a laser down a pitch
at an off-vertical angle is no problem.  Therefore, the 'use clino
weights' option has been invented to give such steeply included legs
less weight when inferring the passage direction.  Note that in a
steeply inclined _passage_, all legs are likely roughly equally
inclined, and therefore roughly equally weighted, so using clino
weights shouldn't affect the inferred direction of travel in that
situation.

_TL;DR: if in doubt try first with the 'use clino weights' option selected._

Note that passage wall data is _inferred_ and any resemblence to 
reality may be pure coincidence: if in doubt, use splays!

### What to do next

Once the data is in QGIS3 one can do various things with it.

For example, features (stations, legs, polygons) can be coloured
by elevation to mimic the behaviour of the `aven` viewer in survex
(hat tip Julian Todd for figuring some of this out).  The easiest way
to do this is to use the `.qml` style files provided in this
repository.  For example to colour legs by depth, open the properties
dialog and under the 'Style' tab, at the bottom select 'Style &rarr;
Load Style', then choose one of the `colour_lines_by_elevation*.qml`
style files.  This will apply a colour scheme to the ELEVATION field
data with an inverted spectral colour ramp.  Use `lines` for legs,
walls, cross sections and traverses; `points` for stations; and
`polygons` for polygons.

Two versions of these style files are provided.

The first version uses a graduated, inverted spectral colour ramp to
colour ranges of ELEVATION.  A small limitation is that these ranges
are not automatically updated to match the vertical range of the
current data set, but these can be refreshed by clicking on 'Classify'
(then 'Apply' to see the changes).

The second version uses a simple marker (line, or fill) with the
colour set by an expression that maps the ELEVATION to a spectral
colour ramp.  There are no ranges here, but rather these styles rely
on _zmin_ and _zmax_ variables being set (see 'Variables' tab under
layer &rarr; Properties).  By matching _zmin_ and _zmax_ between layers
with these styles, one can be assured that a common colouring scheme
is being applied.  A handy way to choose values for _zmin_ and _zmax_ is
to open the statistics panel (View &rarr; Panels &rarr; Statistics
Panel) to check out the min and max values in the ELEVATION field.

Colour legs by date is possible using an expression like
`day(age("DATE1",'1970-01-01'))` (which gives the number of days
between the recorded DATE1 and the given date).  Colour legs by error
is also possible.

Another thing one can do is enable 'map tips', for example to use the
NAME field.  Then, hovering the mouse near a station (or leg) will
show the name as a pop-up label.  For this to work:

* 'View &rarr; Map Tips' should be checked in the main menu;
* the map tip has to be set up to use the NAME field
  ('Properties &rarr; Display') in the relevant layer;
* the layer has to be the currently _selected_ one, though
  it does not have to be displayed.

With a _digital elevation model_ (DEM raster layer) even more
interesting things can be done.  For example one can use raster
interpolation [_how to do this in QGIS3?_] to find the surface elevation at
all the imported stations and save for example to a SURFACE_ELEV
field.  Then, one can use the field calculator to make a
DEPTH field containing the depth below surface, as SURFACE_ELEV minus
ELEVATION.  Stations can be coloured by this, or the information can
be added to the 'map tip', etc.

Three dimensional views can be made with the Qgis2threejs plugin,
usually in combination with a DEM [_or directly in QGIS3?_].  To
render features in 3d _either_ use the ELEVATION attribute to set the
absolute height, _or_ (better) save the imported data to a shapefile
(eg as a GeoPackage) and re-import so that QGIS3 knows about the _z_
dimension data and can pass it on to the plugin to inform the
rendering [_check what happens with QGIS3_].  Passage 'tubes' like
those in aven can be approximately rendered using polygons, with the
base set to floor level and the extruded height set to roof level.  To
do this import the MEAN_UP and MEAN_DOWN fields mentioned above and
use the field calculator to make two new floating point (double)
fields: FLOOR equal to ELEVATION minus MEAN_DOWN, and HEIGHT equal to
MEAN_DOWN plus MEAN_UP.  Then render the polygons with the _z_
co-ordinate as the absolute FLOOR, and extruded height as HEIGHT.

Sample georeferenced survey data can be found in
[`DowProv.3d`](DowProv/DowProv.3d).

The corresponding GeoPackage file is
[`DowProv.gpkg`](DowProv/DowProv.gpkg).

Further notes on cave surveying and GIS are in 
[`cave_surveying_and_GIS.pdf`](cave_surveying_and_GIS.pdf).

### Copying

Code in this repository is licensed under GLP v2:

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see
<http://www.gnu.org/licenses/>.

### Copyright

The .3d file parser is based on a GPL v2 library to handle Survex 3D files (`*.3d`),
copyright &copy; 2008-2012 Thomas Holder, http://sf.net/users/speleo3/; 
see https://github.com/speleo3/inkscape-speleo.

Modifications and extensions copyright &copy; (2019) Patrick B Warren.
