from flask import Flask, render_template, request, send_file
#from werkzeug.utils import send_file
import use_model_tflite as model
import base64
import os
import config
import md5
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = './uploads/'
app.config['MAX_CONTENT_PATH'] = 16 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png']

LUT_FOLDER = app.config['UPLOAD_FOLDER'] + 'luts/'
MODEL_PATH = config.MODEL_PATH

@app.route('/download/<path:filename>')
def download(filename):
    return send_file(LUT_FOLDER+filename)

@app.route("/")
def upload_page():
   return render_template("index.html")

@app.route('/convert/<int:session_id>', methods = ['GET', 'POST'])
def upload_file(session_id):
   if request.method == 'POST':
      blob = request.data[22:]
      filename = str(md5.md5_checksum(blob))[:16]
      imgdata = base64.b64decode(blob)
      img_filename = str(filename)+'.jpg'
      img_path = app.config['UPLOAD_FOLDER'] + img_filename
      with open(img_path, 'wb') as f:
         f.write(imgdata)
      lut_filename = str(filename)+'.cube'
      lut_path = LUT_FOLDER + lut_filename
      if not os.path.isfile(lut_path):
        model.run(img_path, lut_path, MODEL_PATH)
      os.remove(img_path)
      return "/download/"+lut_filename
   return "false";

if __name__ == '__main__':
   app.run(host=config.HOST, debug = config.DEBUG, port=config.PORT)
