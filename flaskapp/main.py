from flask import Flask, render_template, request, Response
from flask import send_file, send_from_directory, safe_join, abort
from flask_uploads import UploadSet, configure_uploads, IMAGES

app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

app.config["UPLOADED_PHOTOS_DEST"] = "./static/img"
configure_uploads(app, photos)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        return render_template('about.html')
    return render_template('about.html')

if __name__ == "__main__":
        app.run(debug=True)