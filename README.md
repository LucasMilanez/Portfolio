# Flask Web Project

This is a simple Flask web application that demonstrates how to set up a basic project structure with HTML and CSS.

## Project Structure

```
flask-web-project
├── app.py
├── static
│   └── css
│       └── style.css
├── templates
│   └── index.html
└── README.md
```

## Setup Instructions

1. **Clone the repository** (if applicable):
   ```
   git clone <repository-url>
   cd flask-web-project
   ```

2. **Create a virtual environment**:
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install the required packages**:
   ```
   pip install Flask
   ```

## Usage

1. **Run the application**:
   ```
   python app.py
   ```

2. **Open your web browser** and go to `http://127.0.0.1:5000/` to see the application in action.

## Project Description

- **app.py**: The main entry point of the application that initializes the Flask app and defines the routes.
- **static/css/style.css**: Contains the CSS styles for the web application.
- **templates/index.html**: The HTML template that is rendered by Flask to display the web page.