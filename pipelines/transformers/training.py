from gloe import transformer, partial_transformer, condition
from pipelines.helpers.files_manager import create_folder, delete_files_on_folder
from pipelines.transformers.exceptions.base import BaseExceptionTransformers

sagemaker_temp_dir = '/tmp/sagemaker'
work_directory = '/tmp/teste'


@transformer
def create_sagemaker_temp_files(_) -> None:
    try:
        create_folder(sagemaker_temp_dir, 0o770)
    except PermissionError as e:
        raise BaseExceptionTransformers(exception=e)
    except Exception as e:
        raise BaseExceptionTransformers("It was not possible to create the sagemaker's temp folder", e)


@transformer
def check_if_metadata_is_available(_) -> None:
    try:
        create_folder(work_directory)
        delete_files_on_folder(work_directory)
    except PermissionError as e:
        raise BaseExceptionTransformers(exception=e)
    except Exception as e:
        raise BaseExceptionTransformers("It was not possible to check if the metadata is available", e)
