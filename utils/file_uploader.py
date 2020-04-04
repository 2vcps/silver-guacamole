# Import MinIO library.
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)
import os

path = '/home/pi/timelapse'
files = []
names = []

# Initialize minioClient with an endpoint and access/secret keys.
minioClient = Minio('10.100.9.86:9000',
                    access_key='minio',
                    secret_key='minio123',
                    secure=False)

# Make a bucket with the make_bucket API call.
try:
    minioClient.make_bucket("pics", location="us-east-1")
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
                if '.jpeg' or '.gif' in file:
                    #names.append(file)
                    #files.append(os.path.join(r, file))
                    obj_path = r.replace("./", "")
                    obj_name = file
                    #obj_name = obj_path.replace("/", "") + file
                    print(obj_name, 'uploaded:', os.path.join(r, file), 'to pics bucket on minio.')
                    minioClient.fput_object('pics', obj_name, os.path.join(r, file))
            
    # except ResponseError as err:
    #     print(err)

