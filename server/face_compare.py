#!/usr/bin/env python2
#
# BlackStone eIT 2017
# Based on:
# Example to compare the faces in two images.
# Mahmoud Srour
# 2017/10/15

import numpy as np
import time

import os
import pickle
import sys
from sklearn.mixture import GMM

import openface


#init
dlibFacePredictor = "/root/openface/models/dlib/shape_predictor_68_face_landmarks.dat"
networkModel = "/root/openface/models/openface/nn4.small2.v1.t7"

trainingImagesPath ="/src/training/images"
alignedImagesPath ="/src/training/aligned-images"
featureImagesPath ="/src/training/feature-images"


class FaceCompare:

    def __init__(self, logger):
        self.logger = logger
        self.logger.info("Initiate openface compare")

        self.imgDim = 96
        self.align = openface.AlignDlib(dlibFacePredictor)
        self.net = openface.TorchNeuralNet(networkModel,  self.imgDim)
        self.classifierModel = "/src/training/feature-images/classifier.pkl"

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

    def getRep2(self, rgbImg, multiple=True):

        if multiple:
            bbs = self.align.getAllFaceBoundingBoxes(rgbImg)
        else:
            bb1 = self.align.getLargestFaceBoundingBox(rgbImg)
            bbs = [bb1]

        if len(bbs) == 0 or (not multiple and bb1 is None):
            raise Exception("Unable to find a face")

        reps = []
        for bb in bbs:
            start = time.time()
            alignedFace = self.align.align(
                self.imgDim,
                rgbImg,
                bb,
                landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
            if alignedFace is None:
                raise Exception("Unable to align image")

            rep = self.net.forward(alignedFace)
            reps.append((bb.center().x, rep))
        sreps = sorted(reps, key=lambda x: x[0])

        return sreps

    def getFacesBounding(self, rgbImg):
        self.logger.info("Call getFacesBounding method")
        start = time.time()
        bbs = self.align.getAllFaceBoundingBoxes(rgbImg)
        self.logger.info("End getting Faces Bounding Box")
        if bbs is None:
            self.logger.info("Unable to find a face Exceptoin")
            raise Exception("Unable to find a face")

        self.logger.info("Face detection took {} seconds.".format(time.time() - start))

        return bbs

    def infer(self, rgbImg, multiple=False):
        with open(self.classifierModel, 'rb') as f:
            if sys.version_info[0] < 3:
                (le, clf) = pickle.load(f)
            else:
                (le, clf) = pickle.load(f, encoding='latin1')
        reps = self.getRep2(rgbImg, multiple)
        results = []
        if len(reps) > 1:
            print("List of faces in image from left to right")
        for r in reps:
            rep = r[1].reshape(1, -1)
            bbx = r[0]
            predictions = clf.predict_proba(rep).ravel()
            maxI = np.argmax(predictions)
            person = le.inverse_transform(maxI)
            confidence = predictions[maxI]
            #if args.verbose:
            #    print("Prediction took {} seconds.".format(time.time() - start))
            if multiple:
                print("Predict {} @ x={} with {:.2f} confidence.".format(person.decode('utf-8'), bbx,
                                                                         confidence))
                results.append({"predict": person.decode('utf-8'), "x": bbx, "confidence": confidence})
            else:
                print("Predict {} with {:.2f} confidence.".format(person.decode('utf-8'), confidence))
            if isinstance(clf, GMM):
                dist = np.linalg.norm(rep - clf.means_[maxI])
                print("  + Distance from the mean: {}".format(dist))

        return results