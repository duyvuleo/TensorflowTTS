import logging
import os
import pytest
import numpy as np
import tensorflow as tf

from tensorflow_tts.models import TFFastSpeech
from tensorflow_tts.configs import FastSpeechConfig

os.environ["CUDA_VISIBLE_DEVICES"] = ""

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s (%(module)s:%(lineno)d) %(levelname)s: %(message)s")


@pytest.mark.parametrize(
    "num_hidden_layers,n_speakers", [
        (2, 1), (3, 2), (4, 3)
    ]
)
def test_fastspeech_trainable(num_hidden_layers, n_speakers):
    config = FastSpeechConfig(num_hidden_layers=num_hidden_layers, n_speakers=n_speakers)

    fastspeech = TFFastSpeech(config, name='fastspeech')
    optimizer = tf.keras.optimizers.Adam(lr=0.001)

    # fake inputs
    input_ids = tf.convert_to_tensor([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]], tf.int32)
    attention_mask = tf.convert_to_tensor([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]], tf.int32)
    speaker_ids = tf.convert_to_tensor([0], tf.int32)
    duration_gts = tf.convert_to_tensor([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]], tf.int32)

    mel_gts = tf.random.uniform(shape=[1, 10, 80], dtype=tf.float32)

    def one_step_training():
        with tf.GradientTape() as tape:
            mel_outputs, duration_outputs = fastspeech(
                input_ids, attention_mask, speaker_ids, duration_gts, training=True)
            duration_loss = tf.keras.losses.MeanSquaredError()(duration_gts, duration_outputs)
            mel_loss = tf.keras.losses.MeanSquaredError()(mel_gts, mel_outputs)
            loss = duration_loss + mel_loss
        gradients = tape.gradient(loss, fastspeech.trainable_variables)
        optimizer.apply_gradients(zip(gradients, fastspeech.trainable_variables))

    for _ in range(10):
        one_step_training()
