#!/usr/bin/env python

"""Copy MP3s to a SoundFly AUX in such a way that the SoundFly plays the MP3s in album order.
"""

import os
import re
import shutil
import sys

import id3reader


MUSIC_SRC_PATH = os.path.abspath('./music')
SOUNDFLY_ROOT_DIR_PATH = os.path.abspath('./soundfly')


def main():
    if not os.path.ismount(SOUNDFLY_ROOT_DIR_PATH):
        sys.exit("Mount the SoundFly SD card on {}".format(SOUNDFLY_ROOT_DIR_PATH))
    clear_dir(SOUNDFLY_ROOT_DIR_PATH)
    src_mp3_path_list = find_mp3s(MUSIC_SRC_PATH)
    sorted_src_mp3_path_list = sorted(src_mp3_path_list, key=id3_sort_key)
    copy_mp3s_and_set_timestamp(sorted_src_mp3_path_list, MUSIC_SRC_PATH, SOUNDFLY_ROOT_DIR_PATH)


def clear_dir(dir_path):
    for item_name in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item_name)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.unlink(item_path)


def find_mp3s(root_path):
    mp3_list = []
    for root_dir_path, dir_list, file_list in os.walk(root_path):
        for file_name in file_list:
            file_path = os.path.join(root_dir_path, file_name)
            if is_mp3(file_path):
                mp3_list.append(file_path)
    return mp3_list


def copy_mp3s_and_set_timestamp(mp3_list, src_root_path, dst_root_path):
    """Iterate over the mp3 files in sorted order and update their atime and mtimes, starting at the epoch and going
    forward one day for each file.
    """
    timestamp = 0
    for mp3_path in mp3_list:
        copy_mp3_and_set_timestamp(mp3_path, src_root_path, dst_root_path, timestamp)
        timestamp += 24 * 60 * 60


def copy_mp3_and_set_timestamp(src_mp3_path, src_root_path, dst_root_path, timestamp):
    mp3_rel_path = src_mp3_path[len(src_root_path) + 1:]
    dst_mp3_path = os.path.join(dst_root_path, mp3_rel_path)
    dst_dir_path = os.path.dirname(dst_mp3_path)
    if not os.path.exists(dst_dir_path):
        print 'Creating dir: {}'.format(dst_dir_path)
        os.makedirs(dst_dir_path)
    print '{} ->\n{}'.format(src_mp3_path, dst_mp3_path)
    shutil.copyfile(src_mp3_path, dst_mp3_path)
    os.utime(dst_mp3_path, (timestamp, timestamp))


def id3_sort_key(mp3_path):
    """Create the sort key for an MP3 file.
    """
    id3r = id3reader.Reader(mp3_path)
    return (
        get_value(id3r, 'performer'),
        get_value(id3r, 'year'),
        get_value(id3r, 'album'),
        get_track(id3r),
        get_value(id3r, 'title'),
        # Provide the original path as a fallback for MP3s with missing or non-unique ID3 tags.
        mp3_path,
    )


def is_mp3(mp3_path):
    try:
        id3reader.Reader(mp3_path)
    except Exception:
        return False
    return True


def get_track(id3r):
    try:
        return int(re.split(r'\D', id3r.getValue('track') or '')[0])
    except ValueError:
        return 0


def get_value(id3r, field_str):
    try:
        return id3r.getValue(field_str).decode('utf8', 'ignore')
    except (id3reader.Id3Error, UnicodeDecodeError):
        return 'Unknown'


if __name__ == '__main__':
    main()
