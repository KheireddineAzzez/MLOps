import absl
import keras_tuner
import tensorflow as tf
from tensorflow import keras
import tensorflow_transform as tft

from tfx import v1 as tfx




NUMERIC_FEATURE_KEYS = [
    'age', 'capital-gain', 'capital-loss',
    'education-num', 'fnlwgt', 'hours-per-week'
]

VOCAB_FEATURE_DICT ={
    'education':16, 'marital-status':7, 'native-country':41,
    'occupation':15, 'race':5, 'relationship':6, 'sex':2,
    'workclass':9
}
LABEL_KEY = 'label'

NUM_OOV_BUCKETS = 2

def transformed_name(key):
    key = key.replace('-', '_')
    return key + '_xf'

def _gzip_reader_fn(filenames):
    
    return tf.data.TFRecordDataset(filenames, compression_type='GZIP')

def _input_fn(file_pattern,tf_transform_output,num_epochs=None,batch_size=128) -> tf.data.Dataset:
    
    transformed_feature_spec =(
        tf_transform_output.transformed_feature_spec().copy()
    )

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







def _get_serve_tf_examples_fn(model, tf_transform_output):
    
    model.tft_layer = tf_transform_output.transform_features_layer()
    
    @tf.function
    def serve_tf_examples_fn(serialized_tf_examples):
        
        feature_spec = tf_transform_output.raw_feature_spec()
        
        
        parsed_features = tf.io.parse_example(serialized_tf_examples, feature_spec)
        
        transformed_features = model.tft_layer(parsed_features)
        
        # get predictions using the transformed features
        return model(transformed_features)
    return serve_tf_examples_fn









def _make_keras_model(hparams: keras_tuner.HyperParameters) -> tf.keras.Model:
  
    num_hidden_layers = hparams.Int('hidden_layers', min_value=1, max_value=5)
    hp_learning_rate = hparams.Choice('learning_rate', values=[1e-2, 1e-3, 1e-4])

    input_numeric = [
        tf.keras.layers.Input(name=transformed_name(colname), shape=(1,), dtype=tf.float32) for colname in NUMERIC_FEATURE_KEYS
    ]

    input_categorical = [
        tf.keras.layers.Input(name=transformed_name(colname), shape=(vocab_size + NUM_OOV_BUCKETS,), dtype=tf.float32) for colname, vocab_size in VOCAB_FEATURE_DICT.items()
    ]

    input_layers = input_numeric + input_categorical


    input_numeric = tf.keras.layers.concatenate(input_numeric)
    input_categorical = tf.keras.layers.concatenate(input_categorical)

    deep = tf.keras.layers.concatenate([input_numeric, input_categorical])

    for i in range(num_hidden_layers):
        num_nodes = hparams.Int('unit'+str(i), min_value=8, max_value=256, step=64)
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





def run_fn(fn_args: tfx.components.FnArgs):

  tensorboard_callback = tf.keras.callbacks.TensorBoard(
        log_dir = fn_args.model_run_dir, update_freq='batch'
    )
 
  tf_transform_output = tft.TFTransformOutput(fn_args.transform_graph_path)

  train_dataset = _input_fn(fn_args.train_files, tf_transform_output, 10)
  eval_dataset = _input_fn(fn_args.eval_files, tf_transform_output, 10)



  if fn_args.hyperparameters:
    hparams = keras_tuner.HyperParameters.from_config(fn_args.hyperparameters)


  model = _make_keras_model(hparams)

  # Write logs to path


  model.fit(
      train_dataset,
      steps_per_epoch=fn_args.train_steps,
      validation_data=eval_dataset,
      validation_steps=fn_args.eval_steps,
      callbacks=[tensorboard_callback]
      )
  signatures = {
        'serving_default':
        _get_serve_tf_examples_fn(model, 
                                 tf_transform_output).get_concrete_function(
                                    tf.TensorSpec(
                                    shape=[None],
                                    dtype=tf.string,
                                    name='examples'))}
  
  model.save(fn_args.serving_model_dir, save_format='tf',signatures=signatures)