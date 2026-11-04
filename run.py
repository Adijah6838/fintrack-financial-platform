from app import create_app

# Create the application instance
app = create_app()

if __name__ == "__main__":
    # Start the development server on port 5000
    app.run(host="127.0.0.1", port=5000)