from flask import Flask, render_template, request
import matplotlib
matplotlib.use('Agg')  # Set the backend to 'Agg'
import matplotlib.pyplot as plt
import io
import numpy as np
import os
import requests

# Before creating the app instance:
os.environ['MPLCONFIGDIR'] = os.path.join(os.getcwd(), ".matplotlib")

app = Flask(__name__)

# Create .matplotlib directory if it doesn't exist
matplotlib_cache_dir = os.environ['MPLCONFIGDIR']
if not os.path.exists(matplotlib_cache_dir):
    os.makedirs(matplotlib_cache_dir)

# Configuration
GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME', 'dimkastaniotis')
GITHUB_REPO_NAME = os.environ.get('GITHUB_REPO_NAME', 'quadratic_graph_code')
GITHUB_FILE_PATH = os.environ.get('GITHUB_FILE_PATH', 'app.py')  # Relative path to the file in the repository
GITHUB_BRANCH = os.environ.get('GITHUB_BRANCH', 'main') #Usually main or master


def get_github_file_content(username, repo_name, file_path, branch="main"):
    """Fetches the content of a file from a GitHub repository."""
    try:
        url = f"https://raw.githubusercontent.com/{username}/{repo_name}/{branch}/{file_path}"
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Σφάλμα κατά την ανάκτηση του αρχείου από το GitHub: {e}"


@app.route('/', methods=['GET', 'POST'])
def quadratic_graph():
    graph_url = None  # Initialize graph_url

    if request.method == 'POST':
        try:
            a = float(request.form['a'])
            b = float(request.form['b'])
            c = float(request.form['c'])

            # Create the graph
            create_graph(a, b, c)
            graph_url = 'static/graph.png'  # Assuming create_graph saves to graph.png

        except ValueError:
            return render_template('index.html', error="Παρακαλώ εισάγετε έγκυρους αριθμούς.")

    return render_template('index.html', graph_url=graph_url)


def create_graph(a, b, c):
    """Creates a graph of the quadratic function and saves it as a PNG image."""
    x = np.linspace(-10, 10, 400)  # Range of x values
    y = a * x**2 + b * x + c

    plt.figure(figsize=(8, 6))  # Adjust figure size if needed
    plt.plot(x, y)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title(f'y = {a:.2f}x^2 + {b:.2f}x + {c:.2f}')  # Format coefficients
    plt.grid(True)

    # Save the graph as a PNG image in the static folder
    graph_path = os.path.join(app.root_path, 'static', 'graph.png')
    plt.savefig(graph_path)
    plt.close()  # Close the plot to free memory


@app.route('/view_code')
def view_code():
    code = get_github_file_content(GITHUB_USERNAME, GITHUB_REPO_NAME, GITHUB_FILE_PATH, GITHUB_BRANCH)
    return render_template('view_code.html', code=code)


if __name__ == '__main__':
    app.run(debug=True)  # Debug mode for development
