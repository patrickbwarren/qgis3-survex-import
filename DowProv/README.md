# Sample georeferenced survey data

This directory contains the cave survey data for the
[Dow Cave - Providence Pot system](http://www.mudinmyhair.co.uk/ "Mud in My Hair")
(Great Whernside, Wharfedale, UK), and is
essentially a snapshot of the data held in the
[Cave Registry Data Archive](http://cave-registry.org.uk/ "Cave Registry"), re-organised into folders.

Note that the `.svx` files have
[unix-style line endings](https://en.wikipedia.org/wiki/Newline "wikipedia")
so on Windows you might have to use something like
[Notepad++](https://notepad-plus-plus.org/ "Notepad++")
to look at them.

Historically Providence Pot was classed as from the entrance to Stalagmite
Corner, and the rest was classed as Dowbergill Passage (or Dowber Gill
Passage), part of Dow Cave -- N. Brindle, CPC Journal 2(1), 4-9 (1955).
The usage here 'Dowbergill Passage' follows Northern Caves vol 1 (1972-9).
In terms of the survey data, Dowbergill Passage splits naturally at 800 yds
chamber, where the WRPC re-survey ended in 2004.
 
Magnetic declinations in individual files were originally calculated
using the International Geomagnetic Reference Field (IGRF) model,
with the online NOAA magnetic declination calculator, for the
location (WGS84) 54.14929 N, 2.04008 W corresponding to SD 97480
72608 (Dowbergill Bridge, just above Kettlewell).  All these
declinations are now commented out, as this method is deprecated in
favour of using the `*declination auto` command.  However it has
been verified that both methods generate the exact same reduced
survey data.

People involved (in alphabetical order):
Steve Barwick, Howard Beck, Simon Beck, David Bradley, Andy Cole,
Peter Lamb, Becka Lawson, Shawn McMinn, Dave Morris, Russel Myers,
Dennis Round, Gareth Sewell (Sweeney), Carmen Smith, Patrick Warren,
Steve Warren, Edward Whitaker, Peter Whitaker.

Clubs involved (in alphabetical order):  
Craven Pothole Club (CPC)  
Red Rose Cave and Pothole Club (RRCPC)  
White Rose Pothole Club (WRPC)

Input CRS fixes are NGR references, relative to the SW corner of
the Ordnance Survey SD grid square, ie SD 000 000.

If the output CRS is EPSG:7405 this is the British National Grid +
ODN heights, and is equivalent to full numeric NGR references.

### Usage and attribution

Please feel free to re-use this cave survey data as you wish provided
you attribute to the caving clubs involved along the lines:

`Based on cave survey data collected 1982-2015, CPC, WRCPC, RRCPC`

For reference cite PB Warren, _The Dow Cave – Providence Pot Resurvey Project_
CPC Record *122*, 11-15 (2016).

A version of this article can also be found 
[online](https://sites.google.com/site/patrickbwarren/caving/dow-cave) 
on my website.

Copyright &copy; (2018-2023) Patrick B Warren, and others.
