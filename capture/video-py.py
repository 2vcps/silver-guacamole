from picamera import PiCamera
from time import sleep
import datetime as dt
# Import MinIO library.
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)
import os
import namegenerator

camera = PiCamera()
now = dt.datetime.now()
date_time = now.strftime("%m_%d_%Y")
def makevid():
    camera.rotation = 270
    camera.resolution = (1920, 1080)
    camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    camera.start_recording('/home/pi/video/{}-{}.h264'.format(namegenerator.gen(), date_time))
    start = dt.datetime.now()
    while (dt.datetime.now() - start).seconds < 10:
        camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        camera.wait_recording(0.2)
    camera.stop_recording()

def uploadvid():
    path = '/home/pi/video'
    files = []
    names = []

# Initialize minioClient with an endpoint and access/secret keys.
    minioClient = Minio('10.100.9.86:9000',
                    access_key='minio',
                    secret_key='minio123',
                    secure=False)

# Make a bucket with the make_bucket API call.
    try:
        minioClient.make_bucket("videos", location="us-east-1")
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
                if '.h264' or '.mp4' in file:
                    #names.append(file)
                    #files.append(os.path.join(r, file))
                    obj_path = r.replace("./", "")
                    obj_name = file
                    #obj_name = obj_path.replace("/", "") + file
                    print(obj_name, 'uploaded:', os.path.join(r, file), 'to videos bucket on minio.')
                    minioClient.fput_object('videos', obj_name, os.path.join(r, file))
    cleantmp()

def cleantmp():
    path = '/home/pi/video'
    files = []
    names = []
    for r, d, f in os.walk(path):
            for file in f:
                if '.mp4' in file:
                    #obj_path = r.replace("./", "")
                    #obj_name = file
                    os.remove( '{}/{}'.format(path, file))
                    print('File {} deleted'.format(file))
                if '.h264' in file:
                    os.remove( '{}/{}'.format(path, file))
                    print('File {} deleted'.format(file))
                    
makevid()

uploadvid()
