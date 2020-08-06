import unittest
from PIL import Image
from numpy import asarray

from src.main.python.classifier.main import predict


class TestPrediction(unittest.TestCase):

    def test_predict_pullover(self):
        image = Image.open("src/test/python/classifier/images/pullover.png")
        data = asarray(image)

        self.assertEqual(predict(data), 'Pullover', "Should predict a pullover")

    def test_predict_trousers(self):
        image = Image.open("src/test/python/classifier/images/trousers.png")
        data = asarray(image)

        self.assertEqual(predict(data), 'Trouser', "Should predict trouser")


if __name__ == '__main__':
    unittest.main()