from optparse import OptionParser
import tensorflow as tf
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.datasets import fashion_mnist
import matplotlib.pyplot as plt


CLASS_NAMES = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

(_, _), (TEST_IMAGES, TEST_LABELS) = fashion_mnist.load_data()


def load(path):
    reconstructed_model = load_model(path)
    probability_model = tf.keras.Sequential([reconstructed_model,
                                             tf.keras.layers.Softmax()])
    return probability_model


model = load("src/main/python/classifier/model/my_h5_model.h5")


def predict(img):
    predictions = _predict(img)
    return CLASS_NAMES[_label(predictions)]


def _predict(img):
    img = np.expand_dims(img, 0)
    predictions = model.predict(img)
    return predictions


def _label(predictions):
    return np.argmax(predictions[0])


def parse_args():
    parser = OptionParser()
    # add options here as needed
    parser.add_option(
        "-t",
        "--test_image",
        action="store",
        type="int",
        dest="test_image"
    )
    return parser.parse_args()


def main():
    (options, args) = parse_args()
    test_image = TEST_IMAGES[options.test_image]
    print("expected label: ", CLASS_NAMES[TEST_LABELS[options.test_image]])

    print("predicted label:", predict(test_image))

    plt.figure()
    plt.imshow(TEST_IMAGES[options.test_image])
    plt.colorbar()
    plt.grid(False)
    plt.show()


if __name__ == '__main__':
    main()
