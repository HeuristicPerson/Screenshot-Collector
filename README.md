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


## Installation and instructions of use

Please, visit the [online wiki](https://github.com/PixelGordo/Screenshot-Collector/wiki) with the updated installation
guide and instructions of use.


## Configuration

To configure both programs, the collector `collect.py` and the mosaic generator `mosaic.py`, you need to edit the file `config.ini` with any plain-text editor. Common programs are gedit in Linux, notepad in Windows (standard program for Mac?, no idea). 

There are three different sections to configure:

1. [`[collector]`](https://github.com/PixelGordo/Screenshot-Collector/wiki/Configuring-image-collector)
2. [`[mosaic]`](https://github.com/PixelGordo/Screenshot-Collector/wiki/Configuring-mosaic-generation)
3. [`[sources]`](https://github.com/PixelGordo/Screenshot-Collector/wiki/Configuring-screenshot-sources)

### \[collector\] section

The basic options for screenshot collector are configured in `config.ini` file, under `[collector]` section. The typical
aspect of that sections is:

    [collector]
    temp_dir   = images/temp-historic   ; Directory for temporal files during collection
    hist_dir   = images/historic        ; Directory for historic images
    hist_ext   = png 

Where the meaning of the parameters are:

* **temp_dir** - Temporary directory for image manipulations after the collection. The source images are copied from the
sources to this directory where they are renamed and converted to the store format. After all the operations, the images
are copied to the historic directory and deleted from this temporary directory.

* **hist_dir** - Historic directory, the place where the processed images are stored (ideally) forever.

* **hist_ext** - Image extension (or format, if you wish) for historic images. If you don't want any kind of quality loss,
`png` should be your preferred format. If you prefer to save more space in your hard drive, `jpg` should your preferred
format.

Image manipulations are done in Screenshot Collector using [Imagemagick](www.imagemagick.org) which is a quite powerful
and popular image manipulation software compatible with most image formats. So maybe you could play with other image
formats than `png` and `jpg`.

### \[mosaic\] section

### \[sources\] section

## Extra

How to properly mount a NTFS partition in Linux to avoid problems with the script

http://ubuntuforums.org/showthread.php?t=1604251

360 background ftp server that works even when playing

http://digiex.net/downloads/download-center-2-0/xbox-360-content/libxenon-homebrew-jtag-reset-glitch-content/9524-ftpdll-0-3-xbox-360-ftp-server-runs-background-dash-game.html