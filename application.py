from flask import Flask, make_response, jsonify, request
from flask_cors import CORS
import cv2, base64, io, os
import numpy as np

application = Flask(__name__)
CORS(application) 

def stitch(read_img, select_mode):
    
    if select_mode == "Scans":
        stitcher = cv2.Stitcher.create(mode=cv2.Stitcher_SCANS)
        print(f"{select_mode}モードで実行")
        
    else:
        stitcher = cv2.Stitcher.create()
        print(f"{select_mode}モードで実行")
        
    result = stitcher.stitch(read_img)
    
    if result[0]==0:
        stitched = result[1]
        
        return stitched, result[0]
    
    elif result[0]==1:
        return None, result[0]

@application.route("/", methods=['GET'])
def index():
   return "Server!"

@application.route("/stitch", methods=['GET','POST'])
def parse():
    if request.method == "POST":
        json = request.get_json()
        data = json["image"]
        mode = json["mode"]
        
        # 受け取ったBase64データをデコード
        read_img = []
        for i in range(len(data)):
            f = data[i]
            img_binary = base64.b64decode(f)
            
            bin_data = io.BytesIO(img_binary)
            file_bytes = np.asarray(bytearray(bin_data.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)
            read_img.append(img)
        read_img = np.array(read_img)
        
        # 画像の重ね合わせ
        stitched, result = stitch(read_img, mode)
        
        # Base64へエンコード
        if result == 0:
            retval, buffer = cv2.imencode('.png', stitched)
            encoded_data = base64.b64encode(buffer).decode("utf-8")
        else:
            encoded_data = None
        res = {
            "base64Data" : encoded_data,
            "isStitched" : result,
        }
        
        return make_response(jsonify(res))

if __name__ == "__main__":
    application.run(debug=False, host='0.0.0.0', port=int(os.environ.get("PORT", 8000)))