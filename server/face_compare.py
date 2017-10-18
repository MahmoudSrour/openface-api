#!/usr/bin/env python2
#
# BlackStone eIT 2017
# Based on:
# Example to compare the faces in two images.
# Mahmoud Srour
# 2017/10/15

import numpy as np
import time

import openface


#init
dlibFacePredictor = "/root/openface/models/dlib/shape_predictor_68_face_landmarks.dat"
networkModel = "/root/openface/models/openface/nn4.small2.v1.t7"

class FaceCompare:

    def __init__(self, logger):
        self.logger = logger
        self.logger.info("Initiate openface compare")

        self.imgDim = 96
        self.align = openface.AlignDlib(dlibFacePredictor)
        self.net = openface.TorchNeuralNet(networkModel,  self.imgDim)

        self.logger.info("dlibFacePredictor: {}".format(dlibFacePredictor))
        self.logger.info("networkModel: {}".format(networkModel))

        np.set_printoptions(precision=2)

        self.logger.info("End Initiation openface compare")

    def compare(self, rgbImg1, rgbImg2):
        self.logger.info("Call compare method")
        d = self.getRep(rgbImg1) - self.getRep(rgbImg2)

        distance = np.dot(d, d)
        self.logger.info("Distance:{}".format(distance))
        return float("{:0.3f}".format(distance))

    def getRep(self, rgbImg):
        self.logger.info("Call getRep method")
        start = time.time()
        bb = self.align.getLargestFaceBoundingBox(rgbImg)
        self.logger.info("End getting Largest Face Bounding Box")
        if bb is None:
            self.logger.info("Unable to find a face Exceptoin")
            raise Exception("Unable to find a face")

        self.logger.info("Face detection took {} seconds.".format(time.time() - start))

        start = time.time()
        alignedFace = self.align.align(self.imgDim, rgbImg, bb,
                                  landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
        if alignedFace is None:
            self.logger.info("Unable to align image Exceptoin")
            raise Exception("Unable to align image")

        self.logger.info("Face alignment took {} seconds.".format(time.time() - start))

        start = time.time()
        rep = self.net.forward(alignedFace)

        self.logger.info("  + OpenFace forward pass took {} seconds.".format(time.time() - start))

        return rep