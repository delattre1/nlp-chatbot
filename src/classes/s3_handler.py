import os
import json
import minio
import traceback
import pandas as pd
from io import BytesIO

from structlog import get_logger
log = get_logger()

class S3Handler:
    def __init__(self, access_key, secret_key, endpoint, bucket, secure):
        self.client = minio.Minio(
            endpoint,
            access_key,
            secret_key,
            secure=secure
        )

        log.info('Success connecting S3', endpoint=endpoint)
        self.bucket = bucket
        self.create_bucket()

    def save_html(self, content, fpath):
        self.client.put_object(
            self.bucket,
            fpath,
            BytesIO(content.encode('utf-8')),
            len(content)
        )

    def read_html(self, fpath):
        obj = self.client.get_object(self.bucket, fpath)
        return obj.data.decode('utf-8')

    def create_bucket(self):
        try:
            exists = self.client.bucket_exists(self.bucket)
            if not exists:
                self.client.make_bucket(self.bucket)
                log.info('Success creating bucket at S3', bucket_name=self.bucket)
            else:
                log.info('Bucket at S3 already exists', bucket_name=self.bucket)
        except Exception as err:
            log.error('Failed to create bucket at S3', bucket_name=self.bucket)
            exit()

    def remove(self, file_path):
        self.client.remove_object(self.bucket, file_path)
        log.info('Removed file from bucket at S3', bucket_name=self.bucket, key=file_path)

    def list_files_recursive(self, folder):
        files = []
        prefix = folder.strip('/') + '/'
        objects = self.client.list_objects(self.bucket, prefix=prefix, recursive=True)
      
        for obj in objects:

            if obj.is_dir:
                continue
              
            # Remove the base folders
            # 'extracted_html/yeehawbrewing.com/author/yeehawadmin.html' -> /author/yeehawadmin.html'  
            relative_object_name = obj.object_name.replace(folder, '')
            files.append(relative_object_name)

        return files

if __name__ == '__main__':
    print('[X] This file is not supposed to be runned manually')
