from kerastuner.engine import base_tuner 
import kerastuner as kt
from numpy import dtype
from tensorflow import keras  

from typing import NamedTuple, Dict, Text, Any 
from tfx.components.trainer.fn_args_utils import FnArgs 
import tensorflow as tf 
import tensorflow_transform as tft 

NUMERIC_FEATURE_KEYS = [
    'age', 'capital-gain', 'capital-loss',
    'education-num', 'fnlwgt', 'hours-per-week'
]

VOCAB_FEATURE_DICT ={
    'education':16, 'marital-status':7, 'native-country':41,
    'occupation':15, 'race':5, 'relationship':6, 'sex':2,
    'workclass':9
}

NUM_OOV_BUCKETS = 2 # Non-negative integer, the number of out-of-vocabulary buckets. All out-of-vocabulary inputs will be assigned IDs in the range

LABEL_KEY = 'label'

def transformed_name(key):
    key = key.replace('-', '_')
    return key + '_xf'

TunerFnResult = NamedTuple('TunerFnResult', [('tuner', base_tuner.BaseTuner),
                                            ('fit_kwargs', Dict[Text,Any])])

stop_early = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10) # when the model validation error dose not increase


def _gzip_reader_fn(filenames):

    return tf.data.TFRecordDataset(filenames, compression_type='GZIP')


# create batch of our input data
def _input_fn(file_pattern,tf_transform_output,num_epochs=None,batch_size=128) -> tf.data.Dataset:
   
    transformed_feature_spec =(
        tf_transform_output.transformed_feature_spec().copy()
    )   #specify the transformed feature


    # create batches of features and labels
    dataset  = tf.data.experimental.make_batched_features_dataset(
        file_pattern=file_pattern,
        batch_size=batch_size,
        features=transformed_feature_spec,
        reader = _gzip_reader_fn,
        num_epochs=num_epochs,
        label_key=transformed_name(LABEL_KEY)
    )

    return dataset

def model_builder(hp):

    num_hidden_layers = hp.Int('hidden_layers', min_value=1, max_value=5) # set the minimum  and the max layer
    hp_learning_rate = hp.Choice('learning_rate', values=[1e-2, 1e-3, 1e-4]) # use the learning to find the best model

    input_numeric = [ # spefcify  the shape of our data which is 1 dimmension
        tf.keras.layers.Input(name=transformed_name(colname), shape=(1,), dtype=tf.float32) for colname in NUMERIC_FEATURE_KEYS
    ] # create   numeric  input layers

    input_categorical = [
        tf.keras.layers.Input(name=transformed_name(colname), shape=(vocab_size + NUM_OOV_BUCKETS,), dtype=tf.float32) for colname, vocab_size in VOCAB_FEATURE_DICT.items()
    ] # create categorical input layer

    input_layers = input_numeric + input_categorical # cancatinate the imput layer

    input_numeric = tf.keras.layers.concatenate(input_numeric)
    input_categorical = tf.keras.layers.concatenate(input_categorical)

    deep = tf.keras.layers.concatenate([input_numeric, input_categorical])# create dense deep network

# we have to give for each node a unique name, if i have a unit2 that node corrspond to the second layer
    for i in range(num_hidden_layers):
        num_nodes = hp.Int('unit'+str(i), min_value=8, max_value=256, step=64)
        deep = tf.keras.layers.Dense(num_nodes,activation='relu')(deep)
        

    output = tf.keras.layers.Dense(1, activation='sigmoid')(deep)

    

    model = tf.keras.Model(input_layers, output)

    model.compile(
        loss='binary_crossentropy',
        optimizer=tf.keras.optimizers.Adam(learning_rate = hp_learning_rate),
        metrics = 'binary_accuracy'
    )

    model.summary()

    return model
# we have to set the tunner strategy, in this we are going to usee hyperBand strategy 
def tuner_fn(fn_args: FnArgs) -> TunerFnResult:
    tuner  = kt.Hyperband(
        model_builder,
        objective='val_binary_accuracy',
        max_epochs=20,
        factor =2,
        directory = fn_args.working_dir,
        project_name = 'kt_hyperband'
    )

    # load transform output
    tf_transform_output = tft.TFTransformOutput(fn_args.transform_graph_path)

    train_set = _input_fn(fn_args.train_files, tf_transform_output, 10) # create 10 batch of data at each model training, make sure that the model will not wait to recieve the data
    val_set = _input_fn(fn_args.eval_files, tf_transform_output, 10)


    return TunerFnResult(
        tuner = tuner,
        fit_kwargs={
            "callbacks":[stop_early],
            "x": train_set,
            "validation_data": val_set,
            "steps_per_epoch": fn_args.train_steps,
            "validation_steps": fn_args.eval_steps
        }
    )