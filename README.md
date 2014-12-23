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

Screenshot sources (the places where you get the screenshots from) are configured in `config.ini` file and you can
add as many as you want. To do so, you just need to add a `[source x]` section, where x is an integer, i.e. 0, 1,
2... For example:

    [source 0]
    name       = Sega Megadrive
    type       = dir
    address    = localhost
    root       = /home/john_doe/.Kega Fusion
    user       =
    password   =
    database   = megadrive
    scheme     = kega
    get_exts   = tga, gif
    del_exts   = txt
    recursive  = no
    clean_dirs = no

The only caution you need to have is avoid the repetition of the x number. `[source 0]`, `[source 1]` and
`[source 2]` are a right group while `[source 0]`, `[source 1]` and `[source 0]` are a wrong group.

Here you can see the meaning of each parameter:

* **name** - The name of the source. Use a descriptive name, it doesn't affect program functionality and it's
just shown when you run the script. Examples of `name` are `Sega Megadrive`, `John's SNES emulator`, `Gameboy
emulator in my laptop`...

* **type** - The type of source. There are three valid types by now: `dir` for directories in the same computer
you are running the program in, `ftp` for FTP servers and `smb` for Samba servers.

* **address** - If the type of the source is `ftp` or `smb`, you indicate here the network address of the
server. It can be an IP like `192.168.0.106` or also a domain name like `my-ftp`. For `dir` sources you don't
need to specify any address but it's a good habit to put `localhost` just to remember it's actually located in
the same computer that's running Screenshot Collector.

* **root** - Here you specify in which folder are located the screenshots inside the *localhost* computer (for
`dir`) or the remote server (`ftp` or `smb`). 

* **user** - Name of the user for FTP and Samba servers.

* **password** - Password to access the FTP and Samba servers.

* **database** - Name of the database of games to use for the screenshot source. Yes, this is a mandatory field,
Screenshot Collector only works if you have the right databases of games. Maybe the biggest drawback of the
program... or maybe a feature. Full explanation about the subject
[here](https://github.com/PixelGordo/Screenshot-Collector/wiki/Game-databases).

* **scheme** - Every emulator or gaming system (i.e. Freestyle Dash for Xbox 360) saves screenshots with a
different name structure. i.e. For emulator A it could be `screenshot 0123 - Super Mario World.png` while for
emulator B it could be `Super Mario World - 01 Apr 2014.gif`. In order to convert those different naming schemes
to the global format used for Screenshot Collector, you need to specify the source scheme. Valid schemes (by
now, more to come in the future) are:

  * `freestyledash` - An unofficial dashboard for Xbox 360  consoles with RGH/JTAG modification
    [homepage](http://www.realmodscene.com/index.php?/forum/36-freestyle-dashboard-f3/).
  * `kega` - An 8-16 bit SEGA consoles emulator
    [homepage](http://www.carpeludum.com/kega-fusion/).
  * `zsnes` - A Nintendo Super Nintendo emulator
    [homepage](http://www.zsnes.com/).

* **get_exts** - File extensions to obtain. You can select as many as you want separating them with commas.
i.e. jpg, gif, bmp.

* **del_exts** - File extensions to delete from the source. Typically, after obtaining the screenshots, you
want to delete them from the source. Again, you can select multiple ones i.e. jpg, bmp.

* **recursive**  - (yes/no) Indicates if you want to scan the root folder recursively or not, trying to find
images in sub-folders of the root folder.

* **clean_dirs** - (yes/no) Indicates if you want to delete the empty sub-folders (just the empty ones) of
the root folder after you get the images with the desired extensions (`get_exts` option) and you delete the
files with desired extensions (`del_exts`).


## Extra

How to properly mount a NTFS partition in Linux to avoid problems with the script

http://ubuntuforums.org/showthread.php?t=1604251

360 background ftp server that works even when playing

http://digiex.net/downloads/download-center-2-0/xbox-360-content/libxenon-homebrew-jtag-reset-glitch-content/9524-ftpdll-0-3-xbox-360-ftp-server-runs-background-dash-game.html