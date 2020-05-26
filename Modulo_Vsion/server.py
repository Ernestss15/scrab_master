
from capture import convert_image
import imageio


def decode_image(img):
    return convert_image(img)


img = imageio.imread("reference4.png", as_gray=False, pilmode="RGB")
decode_image(img)

