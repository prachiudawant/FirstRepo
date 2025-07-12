from flask import Flask, render_template, request, redirect, url_for
from models import db, Todo  # Import db and Todo model from models.py
import os

app = Flask(__name__)

# Configure the database
# We'll use a SQLite database file. For Docker, it's often placed in a volume,
# but for simplicity, we'll put it in the app directory for now.
# In a production setup, you'd use an external database like PostgreSQL or MySQL.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the Flask app
db.init_app(app)

# Create database tables if they don't exist
# This will be run once when the application starts for the first time
# or when the container is built/run.
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """
    Renders the main page, displaying all current to-do items.
    """
    todos = Todo.query.all()
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add_todo():
    """
    Adds a new to-do item to the database.
    """
    content = request.form['content']
    if not content:
        return 'Content cannot be empty!', 400 # Bad request if content is empty

    new_todo = Todo(content=content)
    try:
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback() # Rollback in case of error
        return f"There was an issue adding your todo: {e}", 500 # Internal server error

@app.route('/complete/<int:id>')
def complete_todo(id):
    """
    Marks a to-do item as complete.
    """
    todo = Todo.query.get_or_404(id)
    todo.completed = not todo.completed # Toggle completion status
    try:
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        return f"There was an issue updating your todo: {e}", 500

@app.route('/delete/<int:id>')
def delete_todo(id):
    """
    Deletes a to-do item from the database.
    """
    todo = Todo.query.get_or_404(id)
    try:
        db.session.delete(todo)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        return f"There was an issue deleting your todo: {e}", 500

if __name__ == '__main__':
    # Create a 'templates' directory if it doesn't exist
    # This is where Flask looks for HTML templates.
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create a simple HTML template for the index page
    # In a real app, you'd have more sophisticated templates.
    index_html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>My To-Do App</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Inter', sans-serif; }
            .container { max-width: 600px; }
            .btn {
                @apply px-4 py-2 rounded-lg font-semibold transition duration-200 ease-in-out;
            }
            .btn-primary { @apply bg-blue-500 text-white hover:bg-blue-600; }
            .btn-danger { @apply bg-red-500 text-white hover:bg-red-600; }
            .btn-success { @apply bg-green-500 text-white hover:bg-green-600; }
            .btn-toggle { @apply bg-gray-300 text-gray-800 hover:bg-gray-400; }
            .todo-item {
                @apply flex items-center justify-between p-4 mb-2 bg-white rounded-lg shadow-sm;
            }
            .todo-item.completed .content {
                @apply line-through text-gray-500;
            }
        </style>
    </head>
    <body class="bg-gray-100 flex items-center justify-center min-h-screen">
        <div class="container mx-auto p-6 bg-white rounded-xl shadow-lg">
            <h1 class="text-3xl font-bold text-gray-800 mb-6 text-center">My To-Do List</h1>

            <form action="/add" method="POST" class="flex mb-8">
                <input type="text" name="content" placeholder="Add a new task..."
                       class="flex-grow p-3 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                <button type="submit" class="btn btn-primary rounded-r-lg">Add Task</button>
            </form>

            <div class="space-y-4">
                {% if todos %}
                    {% for todo in todos %}
                        <div class="todo-item {% if todo.completed %}completed{% endif %}">
                            <span class="content text-lg text-gray-700">{{ todo.content }}</span>
                            <div class="flex space-x-2">
                                <a href="{{ url_for('complete_todo', id=todo.id) }}"
                                   class="btn btn-toggle {% if todo.completed %}bg-green-500 text-white hover:bg-green-600{% else %}bg-yellow-500 text-white hover:bg-yellow-600{% endif %}">
                                    {% if todo.completed %}Unmark{% else %}Complete{% endif %}
                                </a>
                                <a href="{{ url_for('delete_todo', id=todo.id) }}" class="btn btn-danger">Delete</a>
                            </div>
                        </div>
                    {% endfor %}
                {% else %}
                    <p class="text-center text-gray-500 text-lg">No tasks yet! Add one above.</p>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """
    with open('templates/index.html', 'w') as f:
        f.write(index_html_content)

    # Run the Flask app
    # host='0.0.0.0' makes the app accessible from outside the container
    app.run(debug=True, host='0.0.0.0', port=5000)

