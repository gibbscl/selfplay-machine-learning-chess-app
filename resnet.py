import tensorflow as tf
from tensorflow import keras


def identity_block(input, filter_num, k_size, stride_num):

    input_shortcut = input

    #First layer in residual block
    input = tf.keras.layers.Conv2D(filters=filter_num, kernel_size=(k_size,k_size), strides=stride_num, activation='relu', padding='same')(input)
    input = tf.keras.layers.BatchNormalization(axis=1)(input)

    input = tf.keras.layers.Add()([input, input_shortcut])
    input = tf.keras.layers.Activation('relu')(input)

    return input


def convolutional_block(input, filter_num, k_size, stride_num):
    input_shortcut = input

    #First layer in residual block
    input = tf.keras.layers.Conv2D(filters=filter_num, kernel_size=(k_size,k_size), strides=stride_num, activation='relu', padding='same')(input)
    input = tf.keras.layers.BatchNormalization(axis=1)(input)

    #Shortcut path
    input_shortcut = tf.keras.layers.Conv2D(filters=filter_num, kernel_size=(k_size,k_size), 
                    strides=stride_num, activation='relu', padding='same')(input_shortcut)
    input_shortcut = tf.keras.layers.BatchNormalization(axis=1)(input_shortcut)

    input = tf.keras.layers.Add()([input, input_shortcut])
    input = tf.keras.layers.Activation('relu')(input)

    return input


def create_resnet():
    model_input = tf.keras.layers.Input(shape=(8, 8, 103))

    #First convolutional layer
    input = tf.keras.layers.Conv2D(filters=256, kernel_size=(3, 3), strides=1, activation='relu', padding='same')(model_input)
    input = tf.keras.layers.BatchNormalization(axis=1)(input)

    #Adding 20 residual blocks each with one convolutional layer each, using a skip-connection
    for _ in range(20):
        #input = convolutional_block(input, 256, 3, 1)
        #input = identity_block(input, 256, 3, 1)
        input = identity_block(input, 256, 3, 1)

    #flat_layer = tf.keras.layers.Flatten()(input)
    
    policy_head = tf.keras.layers.Conv2D(filters=256, kernel_size=(3, 3), strides=1, activation='relu', padding='same')(input)
    policy_head = tf.keras.layers.BatchNormalization(axis=1)(policy_head)
    policy_head = tf.keras.layers.Conv1D(filters=76, kernel_size=(64),activation='relu', padding='same')(policy_head)
    policy_head = tf.keras.layers.Flatten()(policy_head)
    policy_head = tf.keras.layers.Dense(4864)(policy_head)

    value_head = tf.keras.layers.Conv2D(filters=1, kernel_size=(1, 1), strides=1, activation='relu', padding='same')(input)
    value_head = tf.keras.layers.BatchNormalization(axis=1)(value_head)
    value_head = tf.keras.layers.Flatten()(value_head)
    value_head = tf.keras.layers.Dense(1)(value_head)


    model = tf.keras.models.Model(inputs=model_input, outputs=(policy_head, value_head))
    model.summary()
    return model

model = create_resnet()
model.save('.\model')
#model.save("path_to_my_model")
#Recreate the exact same model purely from the file:
#model = keras.models.load_model("path_to_my_model")