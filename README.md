# HebrewWikiDigest 🧠🗂️

**HebrewWikiDigest** is your go-to command-line tool for fetching, processing, and dynamically summarizing Hebrew text from MediaWiki. Whether you’re a student, researcher, or just curious about the Hebrew Wikipedia, HebrewWikiDigest makes it easier than ever to digest large volumes of content by breaking down articles into concise, readable summaries.

## 🚀 Project Overview

HebrewWikiDigest empowers users to interact with Hebrew MediaWiki content directly from the command line. With its advanced text processing and summarization capabilities, this tool is perfect for anyone looking to streamline their research or quickly grasp the essence of extensive articles.

### 🌟 Key Features

- **📥 Fetch MediaWiki Content**: Pull Hebrew articles directly from a MediaWiki database and store them efficiently.
- **📝 Dynamic Summarization**: Transform long articles into concise summaries using advanced natural language processing.
- **🔄 CRUD Operations**: Manage your stored articles with intuitive create, read, update, and delete commands.
- **📊 Logging and Monitoring**: Track your actions and manage your data with detailed logs for every operation.

## 🛠️ Project Structure

- **`main.py`**: The entry point of the application that sets up the environment and initiates the command-line interface.
- **`menus`**: Modules for interactive menus, complete with ASCII art to make the CLI experience engaging and user-friendly.
  - **`main_menu.py`**: Handles the main options and guides users through the app.
  - **`submenu.py`**: Manages navigation between different operational submenus.
- **`operations`**: Core functionalities, including database management and text summarization.
  - **`create_operations.py`**: Handles creating database structures to store page data.
  - **`read_operations.py`**: Fetches and processes pages for summarization.
  - **`summarization.py`**: Implements the core summarization logic using advanced algorithms.
- **`utils`**: Utility scripts for database connections and text processing.
  - **`database_utils.py`**: Manages database setup and connectivity.
  - **`text_processing.py`**: Contains helper functions for cleaning and preparing text.

## 📦 Getting Started

### Prerequisites

- Python 3.8+ installed on your system.
- Required Python packages installed (refer to `requirements.txt`).

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/HebrewWikiDigest.git
   cd HebrewWikiDigest
   ```

2. **Install Dependencies**:
   Use pip to install all required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up the Database**:
   Configure your database connection settings in the `config.py` file located in the `utils` directory.

4. **Run the Application**:
   Start the tool using:
   ```bash
   python main.py
   ```

### Usage

- Navigate through the interactive command-line interface to fetch, summarize, and manage Hebrew MediaWiki articles.
- Choose articles to summarize and get a quick, concise view of their content directly in your terminal.
- Use built-in logging to keep track of your actions and refine your summaries.

## 🌐 Future Enhancements

- **🖥️ Graphical User Interface**: Add a GUI to enhance user interaction and visualization of summaries.
- **📚 Multi-Language Support**: Expand to support more languages, broadening the scope beyond Hebrew.
- **🔍 Advanced Search Capabilities**: Implement search and filter options to find relevant articles faster.

## 🤝 Contributing

Want to make HebrewWikiDigest even better? Contributions are always welcome! Fork the repo, make your changes, and submit a pull request. Let’s build a better summarization tool together! 🚀

## 📜 License

This project is licensed under the MIT License. Check the `LICENSE` file for more details.

## 📧 Contact

Got questions, suggestions, or feedback? Reach out at wh1ter0seunm4sked@gmail.com

