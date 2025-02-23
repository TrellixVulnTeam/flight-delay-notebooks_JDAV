#
# Copyright 2020 IBM Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
from pathlib import Path
import requests
import sys
import tarfile
from urllib.parse import urlparse


def download_from_public_url(url):

    data_dir_name = 'data'

    print('Downloading data file {} ...'.format(url))
    r = requests.get(url)
    if r.status_code != 200:
        raise RuntimeError('Could not fetch {}: HTTP status code {}'.format(url, r.status_code))
    else:
        # extract data set file name from URL 
        data_file_name = Path((urlparse(url).path)).name
        # create the directory where the downloaded file will be stored
        data_dir = Path(data_dir_name)    
        data_dir.mkdir(parents=True, exist_ok=True)
        downloaded_data_file = data_dir / data_file_name

        print('Saving downloaded file "{}" as ...'.format(data_file_name))
        with open(downloaded_data_file, 'wb') as downloaded_file:
            downloaded_file.write(r.content)
    
        if r.headers['content-type'] in ['application/x-tar', 'application/x-gzip']:
            print('Extracting downloaded file in directory "{}" ...'.format(data_dir))
            with tarfile.open(downloaded_data_file, 'r') as tar:
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(tar, data_dir)
            print('Removing downloaded file ...')
            downloaded_data_file.unlink()

if __name__ == "__main__": 
    
    # This script downloads a compressed data set archive from a public location
    # e.g. http://server/path/to/archive and extracts it.
    # The archive location can be specified using the DATASET_URL environment variable
    # DATASET_URL=http://server/path/to/archive.

    # initialize download URL from environment variable
    dataset_url = os.environ.get('DATASET_URL')
    
    # No data set URL was provided.
    if dataset_url is None:
        raise RuntimeError('Cannot run script. A data set URL must be provided as input.')
 
    # Try to process the URL
    download_from_public_url(dataset_url)