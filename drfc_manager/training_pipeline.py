import os
from copy import copy
from io import BytesIO

from gloe import If
from gloe.utils import debug, forward

from drfc_manager.transformers.training import create_sagemaker_temp_files, check_if_metadata_is_available, \
    upload_hyperparameters, upload_metadata, upload_reward_function, upload_training_params_file
from drfc_manager.utils.docker.server import DockerClientServer
from drfc_manager.transformers.general import check_if_model_exists, images_tags_has_some_running_container, \
    echo, forward_condition, copy_object, remove_objects_folder
from drfc_manager.types_built.hyperparameters import HyperParameters
from drfc_manager.types_built.model_metadata import ModelMetadata
from drfc_manager.utils.minio.server import MinioClientServer


_docker_client = DockerClientServer.get_instance()
_minio_client = MinioClientServer.get_instance()
sagemaker_tag = os.getenv('SAGEMAKER_IMAGE_REPOTAG')
robomaker_tag = os.getenv('ROBOMAKER_IMAGE_REPOTAG')
_custom_files_folder = os.getenv('CUSTOM_FILES_FOLDER_PATH')


def train_pipeline(
    model_name: str,
    hyperparameters: HyperParameters,
    model_metadata: ModelMetadata,
    reward_function_buffer: BytesIO,
    overwrite: bool = False
):
    reward_function_obj_location_custom = f'{_custom_files_folder}/reward_function.py'
    reward_function_obj_location_model = f'{model_name}/reward_function.py'

    model_data_to_custom_files = forward[None]() >> (
        (
            upload_hyperparameters(_minio_client, hyperparameters),
            upload_metadata(_minio_client, model_metadata),
            upload_reward_function(_minio_client, reward_function_buffer)
        )
    )

    training_start_pipeline = (
        create_sagemaker_temp_files >>
        check_if_metadata_is_available >>
        images_tags_has_some_running_container(_docker_client, [sagemaker_tag, robomaker_tag]) >>
        forward_condition
        .Then(echo("The training is running, please stop the train before starting a new one."))
        .Else(
            check_if_model_exists(_minio_client, model_name, overwrite) >>
            forward_condition
            .Then(echo("The model already exists, use another name or set `overwrite` param to True!"))
            .Else(
                model_data_to_custom_files >>
                echo('Data uploaded successfully to custom files') >>
                # Removing previous data not working, check if it is required
                # remove_objects_folder(_minio_client, model_name) >>
                # echo('Previous models data was successfully cleaned') >>
                copy_object(_minio_client, reward_function_obj_location_custom, reward_function_obj_location_model) >>
                echo(f'The reward function copied successfully to models folder '
                     f'at {reward_function_obj_location_model}') >>
                upload_training_params_file(_minio_client, model_name) >>
                echo('Upload successfully the RoboMaker training configurations')
            )
        )
    )
    training_start_pipeline(None)
