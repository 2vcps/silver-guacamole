from time import sleep
from datetime import datetime
import subprocess
# Import MinIO library.
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)
import os
from subprocess import CalledProcessError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

path = './'
files = []
names = []

def downloadvid():
    print('Downloading Video from Object Store')
    minioClient = Minio('10.100.9.86:9000',
                    access_key='minio',
                    secret_key='minio123',
                    secure=False)
    objects = minioClient.list_objects("videos", recursive=True)
    for obj in objects:
        print(obj.bucket_name, obj.object_name.encode('utf-8'), obj.last_modified, obj.etag, obj.size, obj.content_type)
        try:
            print(minioClient.fget_object('videos', obj.object_name, './{}'.format(obj.object_name) ))
            convertvid(obj.object_name)
        except ResponseError as err:
            print(err)
    upload_clean()
    
        


def convertvid(video_name):
    print('Converting Video to MP4')
    command = "MP4Box -add {} {}.mp4".format(video_name, os.path.splitext(video_name)[0])
    #print('No conversion today')
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        print('FAIL:\ncmd:{}\noutput:{}'.format(e.cmd, e.output))

def upload_clean():
    print('Copy to processed bucket and clean out temp files')
    minioClient = Minio('10.100.9.86:9000',
                    access_key='minio',
                    secret_key='minio123',
                    secure=False)
    try:
        minioClient.make_bucket("processedvideos", location="us-east-1")
    except BucketAlreadyOwnedByYou as err:
        pass
    except BucketAlreadyExists as err:
        pass
    except ResponseError as err:
        print('you suck')
        raise
    finally:
        for r, d, f in os.walk(path):
            for file in f:
                if '.mp4' in file:
                    obj_path = r.replace("./", "")
                    obj_name = file
                    print(obj_name, 'uploaded:', os.path.join(r, file), 'to pics bucket on minio.')
                    minioClient.fput_object('processedvideos', obj_name, os.path.join(r, file))
                    os.remove(file)
                if '.h264' in file:
                    os.remove(file)
                    print('File {} deleted'.format(file))
                    try:
                        print(file)
                        minioClient.remove_object('videos', file)
                    except ResponseError as err:
                        print("Deletion Error: {}".format(err))
def main():
    while True:
        downloadvid()
        logger.info("Waiting... 30s")
        sleep(30)

if __name__ == "__main__":
    main()
