### VisageSearch
VisageSearch is a Python-based tool that allows users to scrape photographs of a person's face and head from online sources using a simple graphical user interface (GUI). The tool includes built-in legal and compliance checks to ensure users are aware of the potential legal ramifications of scraping images from the web.

## Features
Legal Compliance Modal: A disclaimer modal appears before the user can access the main interface, reminding them of the legal responsibilities associated with web scraping.
Simple GUI: The tool uses tkinter for an easy-to-use interface, where users can search for images, monitor progress, and stop downloads as needed.
Progress Tracking: A progress bar shows the number of images downloaded, allowing users to stop the process at any time.
Organized Storage: Downloaded images are saved in a structured directory format: downloads/{name_of_search}.
File Naming: Images are saved with meaningful filenames: {name_of_search}_image_{number}.jpg.
Prerequisites
Make sure you have Python 3.x installed along with the required libraries. You can install the dependencies via pip.

## Installation
Clone the repository or download the project files.
Navigate to the project directory.
Install the required packages using:

pip install -r requirements.txt

### Running the Application

Run the main script:

python main.py

## Usage
Legal Disclaimer: Upon starting the application, a legal disclaimer modal will appear. You must agree to the terms before proceeding.

Search for Images: Enter the name of the person whose images you want to scrape. The tool will begin downloading images and show progress in the progress bar.

Stop Downloading: If you want to stop the download process at any time, click the "Stop Downloading" button.

View Downloaded Images: The images will be saved in the downloads/{name_of_search} directory, named as {name_of_search}_image_{number}.jpg.

## Requirements
The required Python libraries are listed in requirements.txt:

requests==2.31.0
beautifulsoup4==4.12.2
pillow==10.0.0
tkinter==0.1.0

## Notes
Legal Notice: Web scraping can have significant legal implications, especially when scraping images of individuals without their consent. The user is fully responsible for ensuring compliance with all applicable laws, including GDPR and other privacy regulations.
tkinter Installation: tkinter is included in standard Python distributions, but if you encounter any issues, ensure it is installed properly on your system.
## License
This project is for educational purposes only and is provided "as-is" without any warranties. The author is not responsible for any legal issues that may arise from the use of this tool.