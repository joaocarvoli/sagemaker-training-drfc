from pipelines.types_built.hyperparameters import HyperParameters

import io
import os
from minio import Minio as MinioClient
from minio.error import MinioException
from orjson import dumps, OPT_INDENT_2

from pipelines.types_built.model_metadata import ModelMetadata
from pipelines.utils.minio.exceptions.file_upload_exception import FileUploadException
from dotenv import load_dotenv

load_dotenv()

_bucket_name = os.getenv('BUCKET_NAME')
_custom_files_folder = os.getenv('CUSTOM_FILES_FOLDER_PATH')
_reward_function_path = os.getenv('REWARD_FUNCTION_PATH')


def upload_hyperparameters(
    minio_client: MinioClient,
    hyperparameters: HyperParameters
):
    """
    Uploads hyperparameters to an S3 bucket.

    Args:
        minio_client (MinioClient): The client of the minio api
        hyperparameters (HyperParameters): The hyperparameters to minio.

    Returns:
        bool: True if the minio was successful, False otherwise.
    """
    
    try:
        hyperparameters_serialized = dumps(hyperparameters, option=OPT_INDENT_2)
        object_size = len(hyperparameters_serialized)
        object_name = 'hyperparameters.json'
        
        result = minio_client.put_object(
            _bucket_name,
            f'{_custom_files_folder}/{object_name}',
            io.BytesIO(hyperparameters_serialized),
            length=object_size,
            content_type="application/json"
        )
        
        return True if result else False
    except MinioException:
        raise FileUploadException(message=f'Error uploading {object_name} file to S3 bucket')
    except Exception as e:
        raise FileUploadException(original_exception=e)


def upload_reward_function(
    minio_client: MinioClient
):
    try:
        current_dir = os.getcwd()
        file_path = os.path.join(os.path.dirname(current_dir), _reward_function_path)
        
        with open(file_path, "rb") as fh:
            buf = io.BytesIO(fh.read())
        
        buffer_size = buf.getbuffer().nbytes
        object_name = 'reward_function.py'
        
        result = minio_client.put_object(
            _bucket_name,
            f'{_custom_files_folder}/{object_name}',
            buf,
            length=buffer_size,
            content_type="text/plain"
        )
        
        return True if result else False
    except MinioException:
        raise FileUploadException(message=f'Error uploading {object_name}  file to S3 bucket')
    except Exception as e:
        raise FileUploadException(original_exception=e)


def upload_metadata(
    minio_client: MinioClient,
    model_metadata: ModelMetadata
):
    """
    Uploads metadata to an S3 bucket.

    Args:
        minio_client (MinioClient): The client of the minio api
        model_metadata (Model Metadata): The metadata to minio.

    Returns:
        bool: True if the minio was successful, False otherwise.
    """
    
    try:
        model_metadata_serialized = dumps(model_metadata, option=OPT_INDENT_2)
        object_size = len(model_metadata_serialized)
        object_name = 'model_metadata.json'
        
        result = minio_client.put_object(
            _bucket_name,
            f'{_custom_files_folder}/{object_name}',
            io.BytesIO(model_metadata_serialized),
            length=object_size,
            content_type="application/json"
        )
        
        return True if result else False
    except MinioException:
        raise FileUploadException(message=f'Error uploading {object_name}  file to S3 bucket')
    except Exception as e:
        raise FileUploadException(original_exception=e)