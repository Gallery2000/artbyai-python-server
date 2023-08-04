from flask import Flask, request, jsonify, abort

import glovar
from api import DiscordApi
from utils import verify_hmac_signature

ImageShowType = "show"
ImageShortenType = "shorten"
ImageAskType = "ask"
ImageVariationType = "variation"
ImageGenerateType = "generate"
ImageBlendType = "blend"
ImageDescribeType = "describe"
ImageFastType = "fast"
ImageRelaxType = "relax"
ImageRemixType = "remix"
ImageInfoType = "info"
ImageSettingsType = "settings"
ImagePreferRemixType = "prefer_remix"

app = Flask(__name__)

discord_api = DiscordApi()


@app.route('/trigger/upload_file', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({"code": 1, "msg": "No image file provided."})
    image_file = request.files['image']
    if image_file.mimetype not in ['image/jpeg', 'image/png']:
        return jsonify({"code": 1, "msg": "Invalid image format. Only JPEG and PNG images are supported."})
    pathname, err = discord_api.upload_file(image_file)
    if err is not None:
        return jsonify({"code": 1, "msg": str(err)})
    return jsonify({"code": 0, "msg": "success", "data": pathname})


@app.route('/trigger/get_img_url', methods=['POST'])
def get_img_url():
    if 'image' not in request.files:
        return jsonify({"code": 1, "msg": "No image file provided."})
    image_file = request.files['image']
    if image_file.mimetype not in ['image/jpeg', 'image/png']:
        return jsonify({"code": 1, "msg": "Invalid image format. Only JPEG and PNG images are supported."})
    img_url, err = discord_api.get_img_url(image_file)
    if err is not None:
        return jsonify({"code": 1, "msg": str(err)})
    return jsonify({"code": 0, "msg": "success", "data": img_url})


@app.route('/trigger/midjourney', methods=['POST'])
def midjourney():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("HMAC-SHA256 "):
        abort(401)
    signature = auth_header[len("HMAC-SHA256 "):]
    data = request.get_json()
    message = f"{data['type']}+{data['nonce']}"

    if verify_hmac_signature(message, signature, glovar.secret_key):
        if data["type"] == ImageGenerateType:
            err = discord_api.generate_image(data)
        elif data["type"] == ImagePreferRemixType:
            err = discord_api.prefer_remix(data)
        elif data["type"] == ImageRemixType:
            err = discord_api.image_remix(data)
        elif data["type"] == ImageAskType:
            err = discord_api.ask_question(data)
        elif data["type"] == ImageInfoType:
            err = discord_api.view_information(data)
        elif data["type"] == ImageFastType:
            err = discord_api.switch_to_fast_mode(data)
        elif data["type"] == ImageRelaxType:
            err = discord_api.switch_to_relax_mode(data)
        elif data["type"] == ImageVariationType:
            err = discord_api.image_variation(data)
        elif data["type"] == ImageDescribeType:
            err = discord_api.describe_image(data)
        elif data["type"] == ImageBlendType:
            err = discord_api.blend_images(data)
        elif data["type"] == ImageShortenType:
            err = discord_api.shorten_prompt(data)
        elif data["type"] == ImageShowType:
            err = discord_api.show_image(data)
        elif data["type"] == ImageSettingsType:
            err = discord_api.get_settings(data)
        else:
            return jsonify({"code": 1, "msg": "unknown type"})

        if err is not None:
            return jsonify({"code": 1, "msg": str(err)})

        return jsonify({"code": 0, "msg": "success"})
    else:
        abort(401)
