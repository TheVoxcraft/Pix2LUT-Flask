import tensorflow as tf
import numpy as np
import lut_tools


def load_image(image_path):
    img = tf.keras.preprocessing.image.img_to_array( # not scaled to 0.0-1.0, do in model
        tf.keras.preprocessing.image.load_img(image_path, target_size=(240, 160), interpolation="bicubic")
    )
    #print("img shape:", img.shape)
    return img.reshape(1, img.shape[0], img.shape[1], 3)

def predict_lut(interpreter, imgdata):
    input_index = interpreter.get_input_details()[0]["index"]
    output_index = interpreter.get_output_details()[0]["index"]
    interpreter.set_tensor(input_index, imgdata)
    interpreter.invoke()
    return interpreter.get_tensor(output_index)

def load_model(modelpath):
    return tf.keras.models.load_model(modelpath)

def run(imgpath, cubepath, modelpath):
    interpreter = tf.lite.Interpreter(model_path=str(modelpath))
    interpreter.allocate_tensors()

    lut = predict_lut(interpreter, load_image(imgpath))
    lut = lut.reshape(512, 3)
    lut_buffer = lut_tools.create_file(lut, 8)
    lut_tools.save_to_file(lut_buffer, cubepath)
    return True

if __name__ == '__main__':
    image_test = './jernej-graj-Mcb9AaM7BD4-unsplash.jpg'
    output_cube_path = "tfestimage.cube"

    run(image_test, output_cube_path, "./trained/models/large2-optimized.tflite")
    