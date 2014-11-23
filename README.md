# Screenshot Collector

## Description

*Screenshot Collector* are a couple of scripts, `collect.py` and `mosaic.py`, that allow you to collect, organize and
show in a nice way the screenshots you take while you play video games. The only requisite is that you have access to
those screenshots either through a standard folder in your computer, a shared samba folder in another device, or a FTP
folder in another device.

Ideally, you should install *Screenshot Collector* in a dedicated home server and run it periodically to gather all the
possible screenshots from your multiple gaming devices. If you don't have or you don't want to have a big home server,
you can use a small [Raspberry Pi](http://www.raspberrypi.org/) (~50$ with everything you need) or similar device for
that purpose.


## Requisites

Main system, it should work fine in other operating systems if you are able to fullfill both requisites:

1. **Python 2.x** installed. You can do it in **Linux**, **OSX**, **Windows**... 
2. **Imagemagick** installed and added to the PATH of the system so you can call it from wherever you want.



External Python libraries:

1. Requests library - in Linux `sudo apt-get install python-requests`
2. lxml library - in Linux `sudo apt-get install python-lxml`


## Extra

How to properly mount a NTFS partition in Linux to avoid problems with the script

http://ubuntuforums.org/showthread.php?t=1604251

360 background ftp server that works even when playing

http://digiex.net/downloads/download-center-2-0/xbox-360-content/libxenon-homebrew-jtag-reset-glitch-content/9524-ftpdll-0-3-xbox-360-ftp-server-runs-background-dash-game.html