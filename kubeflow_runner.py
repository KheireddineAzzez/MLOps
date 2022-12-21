import os 
from absl import logging 
from tfx.orchestration.kubeflow import kubeflow_dag_runner 
from pipeline import create_pipeline
import time 
suffix = int(time.time())


PIPELINE_NAME = f'Test_MLOPS_{suffix}'
PIPELINE_ROOT = 'gs://pipelinesproject/metadata'
DATA_PATH = 'gs://pipelinesproject/data'
SERVING_DIR = 'gs://pipelinesproject/models'

def run():
    
    metadata_config = kubeflow_dag_runner.get_default_kubeflow_metadata_config()
    tfx_image = 'gcr.io/mlopsh/mlops_hhn@sha256:684b7d5266c8d2bfa3fdbe76968cfa64d5dd712e29164038d030ae1e5ab9280b'
    runner_config = kubeflow_dag_runner.KubeflowDagRunnerConfig(
        kubeflow_metadata_config=metadata_config, tfx_image=tfx_image
    )

    kubeflow_dag_runner.KubeflowDagRunner(config=runner_config).run(
        create_pipeline(
            pipeline_name=PIPELINE_NAME,
            pipeline_root=PIPELINE_ROOT,
            serving_dir=SERVING_DIR,
            data_path=DATA_PATH
        )
    )


if __name__ == '__main__':
    logging.set_verbosity(logging.INFO)
    run()
