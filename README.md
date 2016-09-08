### Sync MP3 to SoundFly AUX

##### Copy MP3s to a SoundFly AUX MP3 player in such a way that they are played back in album order.

MP3s typically contain a track number which indicates the position of the song on the album from which it originated, enabling players to play the songs in album order. Unfortunately and to the surprise of many, the SoundFly does not play the songs in album order. In fact, it appears not to take track numbers into account at all, instead playing songs in one of these orders:

- Ordered alphabetically by the MP3 file names.
- Ordered by the modified timestamps of the MP3 files.
- Ordered by the physical order in which the MP3 files are stored on the SD card file system.

People arrive at different conclusions as to which of these orderings is being used by their particular player, so it is possible that there are firmware or other differences between the players which factor into the ordering.
 
This is a small script which attempts to cause the SoundFly to play songs in album order by controlling the factors that appear to determine the ordering.

#### Usage

`python copy_mp3_to_soundfly.py <source> <destination>`

`source` is a directory which contains MP3s that will be copied to the SoundFly, and `destination` is the mounted directory of a SoundFly that is directly connected via USB, a USB memory stick or an SD card that will be used with the SoundFly.    

The script will delete all existing files and folders in the destination and copy MP3 files from the source to the destination in such a way that they (hopefully) are played back in album order.

The script recursively scans the source and any subdirectories for MP3s to copy. Processing is based on the Artist, Year, Album and Track ID3 tags and as long as these are present and correct, the structure of any subdirectories, the directory names and MP3 file names in the source are all irrelevant to the end result. However, if ID3 tags are missing or incorrect in such a way that some MP3s would share the same sort key, the script falls back to sorting the involved MP3s by their locations and file names in the source.     

It is necessary for the script to delete all directories and files in the destination as the first step when copying, so MP3s cannot be copied incrementally to the destination by running the script multiple times with different source directories. To copy only selected MP3s, create a new source directory on a regular disk and copy the selected MP3 files there first.

It is up to the user to make sure that all MP3s in the source will fit in the destination. If necessary, create a new source directory and copy only as many MP3s as will fit there.

To add or delete MP3 files in SoundFly, make the desired changes in the source then rerun the script. The full procedure is then performed, deleting all the files in the destination and copying the MP3 files.

##### Important

<aside class="warning">

The script starts by deleting everything in the destination, so make sure to specify the correct destination, or important files may be lost. Make sure that there's nothing on the SoundFly that you want to keep.

</aside>    

#### Implementation

* The source is a directory tree on disk, designated by the user. The destination is a mounted filesystem that will be used by the SoundFly AUX. 

* All files and folders on the destination are deleted (a full format does not appear to be necessary).

* The source is recursively searched, and all files are added to a list, regardless of apparent type or file extension.
 
* Artist, Year, Album and Track ID3 tags are retrieved from each of the files in the list. Files missing the ID3 header or one or more of the tags are dropped from the list (filtering out non-MP3 files and files that cannot be properly sorted). 

* Files are sorted by the retrieved ID3 tags, in Artist, Year, Album, Track order. 

* Files are processed in the sorted order. For each file:

    * If the source file is for a new artist and/or album, a new artist and/or album folder is created on the SoundFly. Artist folders are created in the root and album folders below their artists.
    
    * The destination filename is set as "track - title.MP3", causing files to be sorted by track if they are sorted alphabetically.
    
    * The source MP3 file is copied to its destination album folder and filename.   
    
    * The modified time of the new file on the destination is set to a date and time one day later than the previously copied file. If it's the first file, its modified time is set to the Unix epoch.

