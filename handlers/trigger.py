from flask import Flask, request, jsonify

from api import DiscordApi

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
ImagePreferRemixType = "prefer_remix"

app = Flask(__name__)

discord_api = DiscordApi()


@app.route('/trigger/upload_file', methods=['POST'])
def upload_file():
    data = request.get_json()
    pathname, err = discord_api.upload_file(data.get('name'), data.get('size'), data.get('imgData'))
    if err is not None:
        return jsonify({"code": 1, "msg": str(err)})
    return jsonify({"code": 0, "msg": "success", "data": pathname})


@app.route('/trigger/get_img_url', methods=['POST'])
def get_img_url():
    data = request.get_json()
    img_url, err = discord_api.get_img_url(data.get('name'), data.get('size'), data.get('imgData'))
    if err is not None:
        return jsonify({"code": 1, "msg": str(err)})
    return jsonify({"code": 0, "msg": "success", "data": img_url})


@app.route('/trigger/midjourney', methods=['POST'])
def midjourney():
    data = request.get_json()
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
    else:
        return jsonify({"code": 1, "msg": "unknown type"})

    if err is not None:
        return jsonify({"code": 1, "msg": str(err)})

    return jsonify({"code": 0, "msg": "success"})
