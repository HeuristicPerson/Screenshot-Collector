This is the default directory for historic stored images. The file name will follow this pattern:

    YYYY-MM-DD HH-mm-SS.SS - database game_id - game_title.png

For example:

    2014-11-08 11-17-28.01 - snes 70bb5513 - Mortal Kombat II (USA) (Rev 1).png

Where each part of the pattern means:

* YYYY = Year when you took the screenshot (i.e. 2014).
* MM = Month when you took the screenshot (from 01 to 12).
* DD = Day when you took the screenshot (from 00 to 31).
* HH = Hour when you took the screenshot (from 00 to 23).
* mm = Minute when you took the screenshot (from 00 to 59).
* SS.SS = Second when you took the screenshot with two decimal positions (from 00.00 to 59.99).

database = Name of the database that contains the game. i.e. 'xbox360' You can find the databases in dats directory.
game_id = Unique code of the game in that database. Typically is a CRC32 code for ROMs (no idea about xbox360).
game_title = Title of the game in ascii format, so certain characters could be missing.