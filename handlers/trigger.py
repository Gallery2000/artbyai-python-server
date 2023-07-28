from flask import Flask, request, jsonify

import services

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

api = services.DiscordService()


@app.route('/trigger/midjourney', methods=['POST'])
def get_all_data():
    data = request.get_json()
    if data["type"] == ImageGenerateType:
        err = api.generate_image(data)
    elif data["type"] == ImagePreferRemixType:
        err = api.prefer_remix(data)
    elif data["type"] == ImageRemixType:
        err = api.image_remix(data)
    elif data["type"] == ImageAskType:
        err = api.ask_question(data)
    elif data["type"] == ImageInfoType:
        err = api.view_information(data)
    elif data["type"] == ImageFastType:
        err = api.switch_to_fast_mode(data)
    elif data["type"] == ImageRelaxType:
        err = api.switch_to_relax_mode(data)
    elif data["type"] == ImageVariationType:
        err = api.image_variation(data)
    elif data["type"] == ImageDescribeType:
        err = api.describe_image(data)
    elif data["type"] == ImageBlendType:
        err = api.blend_images(data)
    elif data["type"] == ImageShortenType:
        err = api.shorten_prompt(data)
    elif data["type"] == ImageShowType:
        err = api.show_image(data)
    else:
        return jsonify({"code": 1, "msg": "unknown type"})

    if err is not None:
        return jsonify({"code": 1, "msg": str(err)})

    return jsonify({"code": 0, "msg": "success"})
