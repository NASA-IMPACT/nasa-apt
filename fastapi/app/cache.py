from typing import Optional
from urllib.parse import urlparse, ParseResult

import boto3
import botostubs
from botocore.exceptions import ClientError, UnknownKeyError


class CacheException(Exception):
    pass


class Cache:
    """
    A simple s3 based cache for atbd pdfs. It has no cache invalidation logic, because the app business rules enforce
    only Published atbds should have cached pdfs, and Published atbds cannot be edited. So they are static resources.
    """

    s3_endpoint: ParseResult
    bucket_name: str
    s3_client: botostubs.S3

    def __init__(self, s3_endpoint: str, bucket_name: str):
        """
        Cache constructor
        :param s3_endpoint:
        :type s3_endpoint: str
        :param bucket_name: bucket name
        :type bucket_name: str
        """
        self.s3_endpoint = urlparse(s3_endpoint)
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            "s3", endpoint_url=self.s3_endpoint.geturl()
        )

    def get_file_url(self, key: str) -> Optional[str]:
        """
        Returns s3 url if key is present in cache, or None. The key should be preformatted with the expected filename,
        using the hexdigest as a folder name. e.g. `{hexdigest...}/{alias}.pdf

        :param key: cache key
        :type key: str
        :return: s3 url of pdf
        :rtype: Optional[str]
        :raises CacheException:
        """
        try:
            response = self.s3_client.head_object(
                Key=key, Bucket=self.bucket_name
            )
            if response["ContentLength"] > 0:
                return self.s3_url_for_object(key)
        except UnknownKeyError:
            pass  # cache miss
        except ClientError as e:
            raise CacheException(str(e)) from e
        return None

    def put_file(self, key: str, filename: str) -> str:
        """
        Update the s3 cache with the given key and local pdf_filename. The key should be preformatted with the expected
        filename, using the hexdigest as a folder name. e.g. `{hexdigest...}/{alias}.pdf
        :param key: cache key
        :type key: str
        :param filename: local filename to upload
        :type filename: str
        :return: the s3 url
        :rtype: str
        :raises CacheException:
        """
        try:
            self.s3_client.upload_file(
                filename,
                self.bucket_name,
                key,
                ExtraArgs={"ACL": "public-read"},
            )
        except ClientError as e:
            raise CacheException(str(e)) from e
        return self.s3_url_for_object(key)

    def s3_url_for_object(self, key: str) -> str:
        """
        Construct a s3 url for the object with key. Uses the format http://s3.amazonaws.com/bucket/file
        Suitable for returning to browser or http client.

        :param key: s3 key/filename
        :type key: str
        :return: s3 url
        :rtype: str
        """

        scheme = self.s3_endpoint.scheme
        # workaround for local port forwarding in dev environment
        port = (
            f":{self.s3_endpoint.port}"
            if self.s3_endpoint.port
            else ""
        )
        hostname = (
            "localhost"
            if self.s3_endpoint.hostname == "localstack"
            else self.s3_endpoint.hostname
        )
        return f"{scheme}://{hostname}{port}/{self.bucket_name}/{key}"
