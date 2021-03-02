import tensorflow as tf
from tensorflow import keras

#model.save("path_to_my_model")
#Recreate the exact same model purely from the file:
#model = keras.models.load_model("path_to_my_model")


input = tf.keras.layers.Input(shape=(8, 8, 103))



layer_one = tf.keras.layers.Conv2D(256, (3, 3), strides=1, activation='relu', padding='same')(input)
layer_two = tf.keras.layers.BatchNormalization(axis = 1)(layer_one)


layer_three = tf.keras.layers.Flatten()(layer_two)

policy_head = tf.keras.layers.Dense(4864)(layer_three)
value_head = tf.keras.layers.Dense(1)(layer_three)



model = tf.keras.models.Model(inputs=input, outputs=(policy_head, value_head))


optimizer = tf.keras.optimizers.SGD(
            0.3, 0.9, nesterov=False, name='SGD')
model.compile(
    optimizer='SGD', loss=None, metrics=None, loss_weights=None,
    weighted_metrics=None, run_eagerly=None, steps_per_execution=None)

model.summary()
model.save('.\model')



