import sys
import logging
import datetime
import config
import json
import base64
import threading

from flask import Flask, request, Response
from flask_jsonpify import jsonify

from werkzeug.exceptions import HTTPException

from face_compare import FaceCompare

from utils import image_helper as ih
from gallery import users, adabas


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
    return jsonify(resp), 201


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

    result = json.dumps({'distance': distance, 'verified': distance < config.general['acceptance-compare-distance']})
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
    result = json.dumps({'distance': distance, 'matched': distance < config.general['acceptance-compare-distance']})
    resp = Response(response=result, status=200, mimetype="application/json")
    return resp


@app.route('/recognize', methods=['GET', 'POST'])
def recognize():
    logger.info('Calling recognize api')

    if 'image' not in request.files and 'image' not in request.form:
        return "image param missing, image must be sent either posted file or public image path", 400

    imageHelper = ih.ImageHelper(logger)
    if 'image' in request.files:
        logger.info('Image sent as post file')
        img1 = imageHelper.get_rgb_img_from_req_file(request.files['image'])
    else:
        logger.info('Image sent as public path')
        img1 = imageHelper.get_rgb_img_from_url_path(request.form['image'])

    filter = None
    if 'filter' in request.form:
        filter = request.form['filter']
    logger.info("Filter: {}".format(filter))

    page = 10
    if 'page' in request.form:
        page = int(request.form['page'])
    logger.info("Page: {}".format(page))
    # connect to db and loop through all images to compare

    gallery = adabas.Adabas(config, logger)
    sqls = gallery.getJobs("profiles", filter, page)
    print(sqls)
    matches = []
    threads = []
    pcount = 0
    for s in sqls:
        t = threading.Thread(target=reco, args=(img1, s, matches, pcount))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    logger.info("data count: {}".format(len(matches)))
    logger.info(matches)
    logger.info("Count of processed rows: {}".format(pcount))

    result = json.dumps(matches)
    resp = Response(response=result, status=200, mimetype="application/json")
    return resp


def reco(img1, sql, arr, count):
    logger.info('Reco method')
    g = adabas.Adabas(config, logger)
    count, data = g.getData(sql)

    # Define face compare object
    logger.info('Initiate face comapre & helper objects')
    face_compare = FaceCompare(logger)
    imageHelper = ih.ImageHelper(logger)

    logger.info('Start scan records')
    for row in data:
        try:
            logger.info("Start converting to image from base64")
            img2 = imageHelper.get_rgb_img_from_base64(row[3])
            logger.info('End converting  get_rgb_img_from_base64')
            distance = face_compare.compare(img1, img2)
            logger.info("End getting comapre result: {}".format(distance))
            count = count + 1
            if (distance < config.general['acceptance-compare-distance']):
                arr.append({'cid': row[0], 'distance': distance})
        except:
            e = sys.exc_info()[0]
            logger.error("Error while proccessing data: {}, exception: {}".format(row[0], e))

    return arr


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
