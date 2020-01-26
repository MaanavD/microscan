# imports
import os

import cv2
import numpy as np
import seaborn as sns
import matplotlib
matplotlib.use('agg')

# pylint: disable=no-member

# image preprocessing
def remove_flare(img):
    pass

def remove_curtaining(img, curtain_mask):
    pass

# util functions
def reject_outliers(data, m=2):
    return data

# classes
class Grain:
    def __init__(self, contour):
        self.contour = contour
        self.area = cv2.contourArea(self.contour)
        self.diameter = (4 * self.area / np.pi)**0.5

class MicroStructure:
    def __init__(self, image_path, scale=1000):
        self.image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        self.scale = scale
        self.shape = self.image.shape
        self.num_pixels = len(self.image.flatten())

        self.grains = self.get_grains()
        self.grain_mask = self.get_grain_mask(self.grains)
        self.dark_mask, self.white_mask, self.line_mask = self.get_masks()

        self.dark_fraction = self.compute_phase_fraction(self.dark_mask)
        self.light_fraction = self.compute_phase_fraction(self.white_mask)
        self.line_fraction = self.compute_phase_fraction(self.line_mask)

        try:
            self.average_grain_area = 0.80*sum(reject_outliers([g.area for g in self.grains])) / len(self.grains)
            self.average_grain_diameter = 0.75*sum(reject_outliers([g.diameter for g in self.grains])) / len(self.grains)
        except:
            self.average_grain_area = 0
            self.average_grain_diameter = 0

    def get_masks(self):
        # dark mask
        _, thresh = cv2.threshold(self.image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        kernel = np.ones((3, 3), np.uint8)
        thresh = cv2.erode(thresh, kernel, iterations=6)
        thresh = cv2.dilate(thresh, kernel, iterations=3)

        inv_image = cv2.bitwise_not(thresh)
        contours, _ = cv2.findContours(inv_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        valid_contours = []
        for contour in contours:
            if cv2.contourArea(contour) < 2000:
                valid_contours.append(contour)

        dark_mask = thresh[:]
        dark_mask = cv2.fillPoly(dark_mask, pts=valid_contours, color=0)

        kernel = np.ones((2,2),np.uint8)
        dark_mask = cv2.dilate(dark_mask, kernel, iterations=1)

        # white mask
        inv_image = cv2.bitwise_not(self.image)
        _, thresh = cv2.threshold(inv_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        kernel = np.ones((3, 3), np.uint8)
        thresh = cv2.erode(thresh, kernel, iterations=6)
        thresh = cv2.dilate(thresh, kernel, iterations=3)

        inv_image = cv2.bitwise_not(thresh)
        contours, _ = cv2.findContours(inv_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        valid_contours = []
        for contour in contours:
            if cv2.contourArea(contour) < 1000:
                valid_contours.append(contour)

        white_mask = thresh[:]
        white_mask = cv2.fillPoly(white_mask, pts=valid_contours, color=255)

        kernel = np.ones((2,2),np.uint8)
        white_mask = cv2.dilate(white_mask, kernel, iterations=1)

        # line mask
        line_mask = np.zeros(self.shape, np.uint8)

        for i,(d,w) in enumerate(zip(dark_mask, white_mask)):
            for j,(a,b) in enumerate(zip(d,w)):
                if a or b:
                    line_mask[i][j] = 255

        line_mask = cv2.bitwise_not(line_mask)

        kernel = np.ones((5,5), np.uint8)
        line_mask = cv2.erode(line_mask ,kernel, iterations=3)

        return dark_mask, white_mask, line_mask

    def get_grains(self):
        # amplify edges
        thresh = cv2.adaptiveThreshold(self.image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        _, thresh = cv2.threshold(thresh, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

        kernel = np.ones((1, 5), np.uint8)
        horizontal = cv2.erode(thresh, kernel, iterations=2)

        kernel = np.ones((5, 1), np.uint8)
        vertical = cv2.erode(thresh, kernel, iterations=2)

        edges = horizontal + vertical
        edges = np.array(np.where(edges == 255, 255, 0), np.uint8)

        # dilate
        kernel = np.ones((5,5),np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=1)

        # fill
        inv_image = cv2.bitwise_not(dilated)
        contours, _ = cv2.findContours(inv_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        valid_contours = []
        for contour in contours:
            if cv2.contourArea(contour) < 1e3:
                valid_contours.append(contour)

        fill_image = dilated[:]
        fill_image = cv2.fillPoly(fill_image, pts=valid_contours, color=0)

        kernel = np.ones((2,2),np.uint8)
        fill_image = cv2.dilate(fill_image, kernel, iterations=1)

        # contours
        inv_image = cv2.bitwise_not(fill_image)
        contours, _ = cv2.findContours(inv_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        valid_contours = []
        for contour in contours:
            if cv2.contourArea(contour) > 1e3 and cv2.contourArea(contour) < 1e5:
                valid_contours.append(contour)

        # build grains
        grains = []
        for vc in valid_contours:
            grains.append(Grain(vc))

        return grains

    def get_grain_mask(self, grains):
        grain_mask = np.zeros(self.shape)
        cv2.drawContours(grain_mask, [g.contour for g in self.grains], -1, 255, 1)
        return grain_mask

    def compute_phase_fraction(self, mask):
        pixels = mask.flatten()
        white_pixels = len([p for p in pixels if p])
        fraction = white_pixels / len(pixels)
        return fraction

def imaging_endpoint(image_path, output_dir):
    mc = MicroStructure(image_path)

    base = os.path.basename(image_path).split(".")[0]
    dark_mask_path = os.path.join(output_dir, base + "_dark_mask.png")
    white_mask_path = os.path.join(output_dir, base + "_white_mask.png")
    line_mask_path = os.path.join(output_dir, base + "_line_mask.png")
    grain_mask_path = os.path.join(output_dir, base + "_grain_mask.png")
    distplot_path = os.path.join(output_dir, base + "_distplot.png")

    cv2.imwrite(dark_mask_path, cv2.resize(mc.dark_mask, (350, 350)))
    cv2.imwrite(white_mask_path, cv2.resize(mc.white_mask, (350, 350)))
    cv2.imwrite(line_mask_path, cv2.resize(mc.line_mask, (350, 350)))
    cv2.imwrite(grain_mask_path, cv2.resize(mc.grain_mask, (350, 350)))
    sns_plot = sns.distplot([g.diameter for g in mc.grains])
    sns_plot.get_figure().savefig(distplot_path)
    matplotlib.pyplot.clf()
    cv2.imwrite(distplot_path, cv2.resize(cv2.imread(distplot_path), (350, 350)))

    return {
        "dark_mask_path": dark_mask_path,
        "white_mask_path": white_mask_path,
        "line_mask_path": line_mask_path,
        "grain_mask_path": grain_mask_path,
        "distplot_path": distplot_path,
        "dark_fraction": mc.dark_fraction,
        "light_fraction": mc.light_fraction,
        "line_fraction": mc.line_fraction,
        "average_grain_area": mc.average_grain_area,
        "average_grain_diameter": mc.average_grain_diameter,
    }

# main
if __name__ == "__main__":
    print(imaging_endpoint("../data/base microstructure/image_0.png", "../temp_test"))
