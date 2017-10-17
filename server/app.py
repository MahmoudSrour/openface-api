import logging
import datetime
import config
import json

from flask import Flask, request, Response
from flask_jsonpify import jsonify
from werkzeug.exceptions import HTTPException

from face_compare import FaceCompare

from utils import image_helper as ih
from gallery import users

app = Flask(__name__)

port = 5000
host = '0.0.0.0'

# setup logging
logging.basicConfig(format='%(levelname)s %(asctime)s %(filename)s %(lineno)d: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@app.route('/health-check')
def healthy_check():
    logger.info('Calling healthy-check api')
    resp = {'message': 'Service up on: %s' % str(datetime.datetime.now())}
    return jsonify(resp)


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    logger.info('Calling verify api')
    if 'image' not in request.files and 'image' not in request.form:
        return "image param missing", 400
    if 'subject_id' not in request.form:
        return "subject_id param missing", 400
    logger.info('verify api validation: passed')

    imageHelper = ih.ImageHelper(logger)
    logger.info('Start reading images from request')

    if 'image' in request.files:
        img1 = imageHelper.get_rgb_img_from_req_file(request.files['image'])
    else:
        img1 = imageHelper.get_rgb_img_from_url_path(request.form['image'])

    logger.info("End getting img1 from request")

    users_gallery = users.Users(config, logger)
    img2_path = users_gallery.get(request.form['subject_id'])['ImagePath']
    img2 = imageHelper.get_rgb_img_from_url_path(img2_path)
    logger.info('End getting img2 from request')

    # Define face compare object
    logger.info('Initiate face comapre object')
    face_compare = FaceCompare(logger)
    distance = face_compare.compare(img1, img2)
    logger.info("End getting verify result: {}".format(distance))

    result = json.dumps({'distance': distance, 'verified': distance > 50.0})
    logger.info("Response result: {}".format(result))
    resp = Response(response=result, status=200, mimetype="application/json")
    return resp


@app.route('/compare', methods=['GET', 'POST'])
def compare():
    logger.info('Calling compare api')
    if 'img1' not in request.files:
        return "Img1 param missing", 400
    if 'img2' not in request.files:
        return "Img2 param missing", 400
    logger.info('Compare api validation: both images found')

    logger.info('Initiate image helper object')
    imageHelper = ih.ImageHelper(logger)
    logger.info('End Initiate image helper object')

    logger.info('calling test method: result %s' % imageHelper.test())

    logger.info('Start reading images from request')

    img1 = imageHelper.get_rgb_img_from_req_file(request.files['img1'])
    img2 = imageHelper.get_rgb_img_from_req_file(request.files['img2'])

    # Define face compare object
    logger.info('Initiate face comapre object')
    face_compare = FaceCompare(logger)
    distance = face_compare.compare(img1, img2)

    logger.info("End getting comapre result: {}".format(distance))
    result = jsonify({"distance": distance})
    resp = Response(response=result, status=200, mimetype="application/json")
    return resp

@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code

    resp = Response(response=json.dumps({'error': str(e)}),
                    status=code,
                    mimetype="application/json")
    return resp


if __name__ == '__main__':
    logger.info('start listening on: http://%s:%d ...' % (host, port))
    app.run(host=host, port=port)
