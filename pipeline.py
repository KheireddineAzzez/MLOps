from cmath import pi
from posixpath import split
from tfx.proto import example_gen_pb2
from tfx.orchestration import pipeline 
import os  
from tfx.components import CsvExampleGen 
from tfx.components import StatisticsGen
from tfx.components import SchemaGen 
from tfx.components import ExampleValidator
from tfx.components import Transform 
from tfx.components import Tuner 
from tfx.proto import trainer_pb2
from tfx.dsl.component.experimental.decorators import component
import tfx.v1 as tfx

from tfx.components import Trainer

census_transform_module_file = 'census_transform.py'
tuner_module_file = 'tuner.py'
trainer_file= "model_trainer.py"






def create_pipeline(
    pipeline_name,
    pipeline_root,
    data_path,
    serving_dir,
    beam_pipeline_args = None,
    metadata_connection_config=None
):
    components =[]
    
    output = example_gen_pb2.Output(
        split_config=example_gen_pb2.SplitConfig(splits=[
            example_gen_pb2.SplitConfig.Split(name='train', hash_buckets=8),
            example_gen_pb2.SplitConfig.Split(name='eval', hash_buckets=2)
        ])
    )
    example_gen = CsvExampleGen(input_base=data_path, output_config=output)
    components.append(example_gen)
    
    statistics_gen = StatisticsGen(examples=example_gen.outputs['examples'])
    components.append(statistics_gen)

    schema_gen = SchemaGen(statistics=statistics_gen.outputs['statistics'])
    components.append(schema_gen)
    validator  = ExampleValidator(
        statistics=statistics_gen.outputs['statistics'],
        schema=schema_gen.outputs['schema']
    )
    
    
    
    
    
    components.append(validator)

    transform  = Transform(
        examples=example_gen.outputs['examples'],
        schema=schema_gen.outputs['schema'],
        module_file=os.path.abspath(census_transform_module_file)
    )
    
    
    
    components.append(transform)

    tuner = Tuner(
        module_file=tuner_module_file,
        examples=transform.outputs['transformed_examples'],
        transform_graph=transform.outputs['transform_graph'],
        schema = schema_gen.outputs['schema'],
        train_args=trainer_pb2.TrainArgs(splits=['train'], num_steps=200),
        eval_args=trainer_pb2.EvalArgs(splits=['eval'], num_steps=50)
    )
    components.append(tuner)
    trainer= Trainer(
    module_file=trainer_file,  # Contains `run_fn`.
    examples=transform.outputs['transformed_examples'],
    transform_graph=transform.outputs['transform_graph'],
    schema=schema_gen.outputs['schema'],
    hyperparameters=tuner.outputs['best_hyperparameters'],
    train_args=trainer_pb2.TrainArgs(num_steps=200),
    eval_args=trainer_pb2.EvalArgs(num_steps=50)


    )
    
    components.append(trainer)
    return pipeline.Pipeline(

        pipeline_name=pipeline_name,
        pipeline_root=pipeline_root,
        components=components,
        beam_pipeline_args=beam_pipeline_args,
        metadata_connection_config=metadata_connection_config
    )