from flask import Flask, render_template, request, Response
from flask import send_file, send_from_directory, safe_join, abort
from flask_uploads import UploadSet, configure_uploads, IMAGES

from imaging import imaging_endpoint

app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

app.config["UPLOADED_PHOTOS_DEST"] = "./static/img"
configure_uploads(app, photos)

results_dir = "./static/res/"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/scraper")
def scraper():
    return render_template("scraper.html")

@app.route("/about")
def about():
    return render_template("about.html",  microscan_img_origin = "https://via.placeholder.com/300x300.png", microscan_img_dark = "https://via.placeholder.com/300x300.png", microscan_img_light = "https://via.placeholder.com/300x300.png", microscan_img_line = "https://via.placeholder.com/300x300.png", microscan_img_dist = "https://via.placeholder.com/300x300.png", microscan_img_grain = "https://via.placeholder.com/300x300.png")

@app.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        image_path = app.config["UPLOADED_PHOTOS_DEST"] + "/" + filename
        results = imaging_endpoint(image_path, results_dir)

        dark_mask = "." + results['dark_mask_path']
        white_mask = "." + results['white_mask_path']
        line_mask = "." + results['line_mask_path']
        grain_mask = "." + results['grain_mask_path']
        dist_plot = "." + results['distplot_path']
        
        
        dark_frac = round(results['dark_fraction']*1000)/1000
        light_frac = round(results['light_fraction']*1000)/1000
        line_frac = round(results['line_fraction']*1000)/1000
        grain_A = round(results['average_grain_area']*1000)/1000
        grain_D = round(results['average_grain_diameter']*1000)/1000



        return render_template('about.html', microscan_img_origin = image_path, microscan_img_dark = dark_mask, microscan_img_light = white_mask, microscan_img_line = line_mask, microscan_img_dist = dist_plot, microscan_img_grain = grain_mask, microscan_num_diam = grain_D, microscan_num_area = grain_A, microscan_num_pfline = line_frac, microscan_num_pflight = light_frac, microscan_num_pfdark = dark_frac)
    return render_template('about.html')

@app.route('/about', methods=['POST'])
def click():
    print("callback test")
    return render_template('about.html')

if __name__ == "__main__":
        app.run(debug=True)
