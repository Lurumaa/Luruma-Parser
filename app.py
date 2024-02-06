from flask import Flask, render_template, request, redirect, url_for
import csv
import os

app = Flask(__name__)

current_csv_path = 'example.csv'
previous_titles = []
previous_years = []

@app.route('/')
def index():
    global current_csv_path, previous_titles, previous_years
    error_message = None

    if current_csv_path:
        try:
            with open(current_csv_path, 'r') as csv_file:
                reader = csv.DictReader(csv_file, delimiter=';')

                # Проверка целостности
                if 'Actor' not in reader.fieldnames:
                    raise KeyError("Actor column not found")

                # Продолжение парсинга
                movies = parse_csv(current_csv_path, 'Nicholson, Jack')
                previous_titles = [movie['Title'] for movie in movies]
                previous_years = [movie['Year'] for movie in movies]

                return render_template('index.html', titles=previous_titles, years=previous_years, error_message=error_message)

        except FileNotFoundError:
            error_message = "File not found. Please upload a valid CSV file."
        except KeyError:
            error_message = "Wrong file chosen. No 'Actor' column."
        except Exception as e:
            error_message = f"Error: {str(e)}"

    return render_template('index.html', titles=previous_titles, years=previous_years, error_message=error_message)

@app.route('/upload', methods=['POST'])
def upload():
    global current_csv_path
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:
        if not os.path.exists('uploads'):
            os.makedirs('uploads')
        
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        # Обновление пути к csv 
        current_csv_path = file_path

        return redirect(url_for('index'))

def parse_csv(file_path, actor_name):
    with open(file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=';')

        movies = []
        for row in reader:
            if actor_name in row['Actor']:
                movies.append({'Title': row['Title'], 'Year': row['Year']})
        return movies

if __name__ == '__main__':
    app.run(debug=True)
