#!/usr/bin/env python2
"""
Log Puzzle exercise

Copyright 2010 Google Inc.
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0

Given an Apache logfile, find the puzzle URLs and download the images.

Here's what a puzzle URL looks like (spread out onto multiple lines):
10.254.254.28 - - [06/Aug/2007:00:13:48 -0700] "GET /~foo/puzzle-bar-aaab.jpg
HTTP/1.0" 302 528 "-" "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US;
rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6"
"""
__author__ = '''Jordan Kubista with help from programmer.ink on initial setup of
                a callback for url retrieve,
        https://programmer.ink/think/how-to-use-urlretrieve-in-python-3.html
                stackoverflow, geeksforgeeks, w3schools and python docs'''

import os
import re
import sys
import urllib.request
import argparse
import time
import webbrowser


def read_urls(filename):
    """Returns a list of the puzzle URLs from the given log file,
    extracting the hostname from the filename itself, sorting
    alphabetically in increasing order, and screening out duplicates.
    """
    with open(filename, 'r') as log:
        read_log = log.read()

        search_host = re.search(r'[^_]+\.\w+', filename)
        search_log = re.findall(r'GET\s(\S+puzzle\S+)\sHTTP', read_log)

        search_urls = []
        for url in search_log:
            full_url = 'http://' + search_host.group() + url
            if full_url not in search_urls:
                search_urls.append(full_url)

# Functions for key to sort full paths in sorted, depending on url format.
        def sort_urls(url):
            return url[-10:]

        def sort_urls_long(url):
            return url[-8:]

        if len(search_urls[0]) == 81:
            sorted_urls = sorted(search_urls, key=sort_urls)
        elif len(search_urls[0]) == 86:
            sorted_urls = sorted(search_urls, key=sort_urls_long)
        return sorted_urls


def data_progress(a, b, c):
    '''Callback function
    @a:Downloaded data block
    @b:Block size
    @c:Size of the remote file
    '''

    per = 100.0*a*b/c

    if per > 100:
        per = 100

    if per == 0:
        print('--------')

    print('Downloading file... %.2f%%' % per)


def file_count(loop_count):
    '''Counts the number of files downloaded
        in the download_images function to help
        with data validation in data_progress'''

    num_files = loop_count + 1
    print(f'--------\nTotal files downloaded {num_files}')


def download_images(img_urls, dest_dir):
    """Given the URLs already in the correct order, downloads
    each image into the given directory.
    Gives the images local filenames img0, img1, and so on.
    Creates an index.html in the directory with an <img> tag
    to show each local image file.
    Creates the directory if necessary.
    """
#  Handles directory creation and file removal with user input.
    if os.path.isdir(dest_dir) is False:
        os.makedirs(dest_dir)
    else:
        files_in_directory = len(os.listdir(dest_dir))
        if files_in_directory > 0:
            print(f'This directory already contains {files_in_directory} files\
 would you like to delete them, if not please name a new directory.')
            answer = input('should we put Thanos on it? (y/n): ')
            if answer == 'y':
                for file in os.listdir(dest_dir):
                    os.remove(os.path.abspath(f'{dest_dir}/{file}'))
                    print(f'Removing... {file}')
            elif answer == 'n':
                new_dir_name = \
                    input('''What should we call this new directory: ''')
                print(f'Creating {new_dir_name} Directory...')
                time.sleep(.5)
                dest_dir = new_dir_name
                if os.path.isdir(dest_dir) is False:
                    os.makedirs(dest_dir)
                else:
                    dest_dir = f'{dest_dir}-dup'
                    os.makedirs(dest_dir)
                    print(f'''That directory name already exists your files will
                           go to {dest_dir}''')
                    time.sleep(2)
# Downloads and saves files to selected directory.
    for index, url in enumerate(img_urls):
        urllib.request.urlretrieve(url, f'{dest_dir}/img{index}',
                                   reporthook=data_progress)
        file_count(index)
    urllib.request.urlcleanup()
    dir_path = os.path.abspath(dest_dir)
    print(f'Completed download to {dir_path}')

# Creates html page with the images to view the full picture.
    with open(f'{dest_dir}/index.html', 'w') as index:
        w = index.write
        w('<html>\n')
        w('<body>\n')
        w('<div style="display: flex;justify-content: center;" >\n')

        total_urls = len(img_urls)
        count = 0
        base_path = os.getcwd()
        for file in range(0, total_urls):
            w(f'<img src="{base_path}/{dest_dir}/img{count}">')
            count += 1
        w('\n</div>\n')
        w('</body>\n')
        w('</html>\n')

# Opens created HTML file in browser when completed.
    file_path = os.path.abspath(dest_dir)
    full_path = file_path + '/' + 'index.html'
    webbrowser.open(f'file:///{full_path}', new=0)


def create_parser():
    """Creates an argument parser object."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--todir',
                        help='destination directory for downloaded images')
    parser.add_argument('logfile', help='apache logfile to extract urls from')

    return parser


def main(args):
    """Parses args, scans for URLs, gets images from URLs."""
    parser = create_parser()

    if not args:
        parser.print_usage()
        sys.exit(1)

    parsed_args = parser.parse_args(args)

    img_urls = read_urls(parsed_args.logfile)

    if parsed_args.todir:
        download_images(img_urls, parsed_args.todir)
    else:
        print('\n'.join(img_urls))


if __name__ == '__main__':
    main(sys.argv[1:])
