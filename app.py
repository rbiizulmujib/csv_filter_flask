from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return redirect(url_for('display', filename=filename))
    return render_template('index.html')

@app.route('/display/<filename>', methods=['GET', 'POST'])
def display(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv(file_path)
    
    # Filtering based on form input
    favs_min = request.args.get('favs_min', '')
    listing_age_max = request.args.get('listing_age_max', '')
    
    if favs_min:
        df = df[df['favs'] > int(favs_min)]
    if listing_age_max:
        df = df[df['listing_age'] < int(listing_age_max)]

    # Sorting based on form input
    sort_by = request.args.get('sort_by', 'listing_age')
    sort_order = request.args.get('sort_order', 'desc')
    if sort_by in df.columns:
        df = df.sort_values(by=sort_by, ascending=(sort_order == 'asc'))

    data = df.to_dict(orient='records')
    columns = df.columns.tolist()
    return render_template('display.html', data=data, columns=columns, filename=filename, favs_min=favs_min, listing_age_max=listing_age_max, sort_by=sort_by, sort_order=sort_order)

if __name__ == '__main__':
    app.run(debug=True)
