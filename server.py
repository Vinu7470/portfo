from flask import Flask, render_template, redirect, url_for, request
import jinja2
import csv

app = Flask(__name__)
print(__name__)

@app.route("/")
def my_home():
    return render_template('index.html')

@app.route('/<string:page_name>')
def html_page(page_name):
    """
    Renders the template corresponding to the given page_name.
    Note: Access these routes WITHOUT the .html extension in the URL.
    """
    try:
        return render_template(f'{page_name}.html')
    except jinja2.exceptions.TemplateNotFound:
        return render_template('404.html'), 404 # Return a 404 error

@app.route('/<string:page_name>.html') #Optional redirect.
def redirect_page(page_name):
    return redirect(url_for('html_page', page_name=page_name))

def write_to_file(data):
    with open('database.txt', mode='a') as database:
        email = data["email"]
        subject = data["subject"]
        message = data["message"]
        file = database.write(f'\n{email},{subject},{message}')

def write_to_csv(data):
    with open('database.csv', mode='a') as database2:
        email = data["email"]
        subject = data["subject"]
        message = data["message"]
        csv_writer = csv.writer(database2, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([email,subject,message])

@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    if request.method == 'POST':
        data = request.form.to_dict()
        write_to_csv(data)
        return redirect(url_for('thankyou')) # Corrected redirect
    else:
        return 'wrong!'

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')
