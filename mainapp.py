from kivy.app import App # Main Kivy app class
from kivy.uix.boxlayout import BoxLayout # Layout for organizing UI elements
import os # Operating system library for file and folder operations
import pandas as pd # Data analysis library for handling data structures like DataFrames
import matplotlib.pyplot as plt # Data visualization library for creating graphs
from kivy.graphics.texture import Texture # Kivy class for handling textures in images
from kivy.uix.image import Image # Kivy Image widget for displaying images
from io import BytesIO # IO class for handling byte streams
from kivy.core.window import Window # Kivy class for handling application window
from kivy.uix.popup import Popup # Kivy class for creating Popup windows
from kivy.uix.button import Button # Kivy class for creating Button widgets
from kivy.uix.filechooser import FileChooserIconView # Kivy file browser widget
from kivy.config import Config # Kivy configuration module
from PIL import Image as PilImage # Python Imaging Library for image manipulation
from PIL import ImageOps
import numpy as np # Scientific computing library for handling arrays and mathematical functions
import pickle # Library for serializing and deserializing Python objects
from google_auth_oauthlib.flow import InstalledAppFlow # Google API OAuth 2.0 authentication library
from googleapiclient.discovery import build # Google API library for creating and interacting with API services
from googleapiclient.errors import HttpError # Google API library for handling API errors
from google.auth.transport.requests import Request # Google API library for making authorized API requests
from kivy.properties import StringProperty # Kivy property class for handling dynamic string values
import datetime # Library for working with dates and times
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from kivy.uix.label import Label

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('googleapiclient')

# Get the directory containing the mainapp.py script
script_directory = os.path.dirname(os.path.abspath(__file__))

# Create an absolute path for the credentials.json file
credentials_path = os.path.join('/Users/sanghoonchung/kivynew/dist/', 'credentials.json')
#set up to throw the error like no time or amplitude varibale
Config.set('kivy', 'keyboard_mode', 'systemanddock')
# Define a custom class named MainLayout that inherits from Kivy's BoxLayout class.
# This class is intended to be the main layout for the application.
class MainLayout(BoxLayout):
    pass
# Define a custom class named FileChooser that inherits from Kivy's FileChooserIconView class.
# This class is intended to create a custom file browser widget with a "Save" button.
class FileChooser(FileChooserIconView):
    def __init__(self, **kwargs):# Initialize the class and create the "Save" button.
        super(FileChooser, self).__init__(**kwargs)# Call the parent class constructor with the given keyword arguments.
        save_button = Button(text="Save", size_hint_y=None, height=30) # Create a "Save" button with specific size and height.
        save_button.bind(on_release=self.save_button_pressed) # Bind the button's on_release event to the save_button_pressed method.
        self.add_widget(save_button) # Add the "Save" button to the FileChooser widget.

    def save_button_pressed(self, instance): # Define the method to be called when the "Save" button is pressed.
        if self.selection: # Check if any file is selected in the FileChooser.
            self.dispatch('on_submit', self.selection)# Dispatch the 'on_submit' event with the selected file(s) as its argument.

class MainApp(App):# Define a custom class named MainApp that inherits from Kivy's App class.
    
    # Initialize the class with additional attributes and set the user data directory.
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        self.current_fig = None
        self.drive_service = None
        self.app_user_data_dir = os.path.dirname(self.get_application_config())
    # When the app starts, authenticate Google Drive credentials, build the service, and list files from Google Drive.
    def on_start(self):
        creds = authenticate_credentials()
        self.drive_service = build('drive', 'v3', credentials=creds)
        self.list_drive_files()
    def build(self):# Build the app's main layout and set the window's soft input mode.
        Window.soft_input_mode = "below_target"
        return MainLayout()
    # List files from Google Drive and download them to the local directory.
    def list_drive_files(self):
        if not self.drive_service:# If Google Drive service is not available, return immediately.
            return
        # List files from Google Drive using the custom list_files function.
        items = list_files(self.drive_service)
        file_chooser = self.root.ids["file_chooser"]
        file_chooser.path = os.path.join(self.app_user_data_dir, "GoogleDrive")
        # Create the GoogleDrive directory if it doesn't exist.
        if not os.path.exists(file_chooser.path):
            os.makedirs(file_chooser.path)
        # Iterate through the items, get the file ID and name, and define the local file path.
        for item in items:
            file_id = item['id']
            file_name = item['name']
            file_path = os.path.join(file_chooser.path, file_name)
            # If the local file doesn't exist, download it from Google Drive.
            if not os.path.exists(file_path):
                request = self.drive_service.files().get_media(fileId=file_id)
                file_data = request.execute()
                # Save the downloaded file data to the local file.
                with open(file_path, "wb") as f:
                    f.write(file_data)

    def open_csv_files(self, filepaths):# Open and process CSV files, display their graphs and calculate statistics.
        if len(filepaths) > 3: # Limit the number of files to process to a maximum of 3.
            filepaths = filepaths[:3]
        # Get a reference to the graph container in the main layout and clear its widgets.
        graph_container = self.root.ids["graph_container"]
        graph_container.clear_widgets()
        max_fft_amplitude = 0
        result = "Yes"
        explosion_time = "N/A"
        self.dataframes = []

        for filepath in filepaths:# Iterate through the filepaths and process each CSV file.
            try:
                df = pd.read_csv(filepath)
                if "time" not in df.columns or "amplitude" not in df.columns:
                    raise ValueError("The CSV file must contain 'time' and 'Amplitude' columns.")
                    continue
            except ValueError as e:
                error_label = Label(text=str(e))
                graph_container.add_widget(error_label)
                print(e)
                continue
            df_filtered = df 
            fig, ax = plt.subplots()
            df.plot(x="time", y="amplitude", ax=ax)
            # Calculate FFT
            fft_vals = np.abs(np.fft.fft(df['amplitude']))
            fft_freqs = np.fft.fftfreq(len(df), 1.0 / 20000.0)
            max_fft_amplitude = fft_freqs[np.argmax(fft_vals)]
            
            
            max_value, min_value, avg_value, max_fft_amplitude, result = self.calculate_statistics(df_filtered)


            if max_value < 200:
                result = "No"

            # Update labels with FFT and result
            self.root.ids["max_fft_amplitude"].text = f"Max FFT: {max_fft_amplitude:.3f}"# change as dominant FFT
            self.root.ids["result_label"].text = f"Result: {result}"
            self.root.ids["timestamp_label"].text = f"Explosion Time: {explosion_time}"
            

        # Save the figure to a buffer in PNG format
            self.current_fig = fig
            buf = BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)

        # Load the image data from the buffer using PIL.Image
            image_data = PilImage.open(buf)

        # Flip the image vertically
            image_data = ImageOps.flip(image_data)

        # Convert the image to RGBA format
            image_data = image_data.convert('RGBA')

        # Create the texture from the image data
            texture = Texture.create(size=(image_data.width, image_data.height))
            texture.blit_buffer(image_data.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
            # Close the buffer and the pyplot figure.
            buf.close()
            plt.close(fig)
            img = Image(texture=texture, allow_stretch=True)
            graph_container.add_widget(img)
    def show_error_popup(self, message):
        error_popup = Popup(title="Error", content=Label(text=message), size_hint=(0.8, 0.3))
        error_popup.open()   

    def calculate_statistics(self, df):# Calculate statistics of a given DataFrame and return the results.
        #(Code for calculating statistics and returning the results)
        max_fft_amplitude = 0
        result = "Yes"
        explosion_time = 0
        max_value = df['amplitude'].max()
        min_value = df['amplitude'].min()
        avg_value = df['amplitude'].mean()
        # Compute FFT
        
        signal = df['amplitude'].to_numpy()
        fft_vals = np.abs(np.fft.fft(df['amplitude']))
        fft_freqs = np.fft.fftfreq(len(df), 1.0 / 1000.0)
        max_fft_amplitude = fft_freqs[np.argmax(fft_vals)]
        # Check if amplitude is over 200
        
        if max_value < 200:
            result = "No"
        else:
            explosion_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return max_value, min_value, avg_value, max_fft_amplitude, result


    def apply_time_range_filter(self, filepaths, start_time, end_time):# Apply a time range filter to the CSV files and update the graphs.
        if not filepaths or not start_time or not end_time:# Return if filepaths or time range is not provided.
            return
        # Convert start_time and end_time to float values
        start_time = float(start_time)
        end_time = float(end_time)
        # Get a reference to the graph container in the main layout and clear its widgets.
        graph_container = self.root.ids["graph_container"]
        graph_container.clear_widgets()

        max_fft_amplitude = 0
        result = "Yes"
        # Iterate through the filepaths and process each CSV file with the time range filter applied.
        for filepath in filepaths:
            df = pd.read_csv(filepath)# Read CSV file into a pandas DataFrame.
            df_filtered = df[(df["time"] >= start_time) & (df["time"] <= end_time)]# Filter the DataFrame based on the provided time range.
            # Plot the filtered DataFrame and calculate statistics.
            fig, ax = plt.subplots()
            df_filtered.plot(x="time", y="amplitude", ax=ax)
            max_value, min_value, avg_value, max_fft_amplitude, result = self.calculate_statistics(df_filtered)
            # Update UI labels with calculated statistics.
            self.root.ids["max_value_label"].text = f"Max: {max_value:.3f}"
            self.root.ids["min_value_label"].text = f"Min: {min_value:.3f}"
            self.root.ids["avg_value_label"].text = f"Avg: {avg_value:.3f}"
            self.root.ids["max_fft_amplitude"].text = f"Max FFT Amp: {max_fft_amplitude:.3f}"
            self.root.ids["result_label"].text = f"Result: {result}"
            
            # Save the figure to a buffer in PNG format
            self.current_fig = fig
            buf = BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)

            image_data = PilImage.open(buf)# Load the image data from the buffer using PIL.Image
            image_data = ImageOps.flip(image_data)# Flip the image vertically
            image_data = image_data.convert('RGBA')# Convert the image to RGBA format

            texture = Texture.create(size=(image_data.width, image_data.height))# Create the texture from the image data
            texture.blit_buffer(image_data.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
            # Close the buffer and the pyplot figure.
            buf.close()
            plt.close(fig)
            img = Image(texture=texture, allow_stretch=True)
            graph_container.add_widget(img)



    def save_graph(self):# Save the current graph to a file.
        def on_submit(instance, filepath, *args):# Define callback functions for the file chooser popup.
            save_file(filepath)
            popup.dismiss()

        def save_file(filepath):
            if not filepath:
                return
            filepath = filepath[0]
            if not filepath.endswith(".png"):
                filepath += ".png"
            self.current_fig.savefig(filepath)

        popup = Popup(title="Save File")# Create a file chooser popup and bind callback functions.
        file_chooser = FileChooserIconView(path=self.app_user_data_dir)


        file_chooser.bind(on_submit=on_submit)
        popup.content = file_chooser
        popup.open()


    def save_file(self, instance, filepath, *args):# Save the current graph to a file (alternative version, used as a callback function).
        if not filepath:
            return
        filepath = filepath[0]
        if not filepath.endswith(".png"):
            filepath += ".png"
        self.current_fig.savefig(filepath)
def authenticate_credentials():# Authenticate Google Drive API credentials.
    creds = None
    token_path = 'token.pickle'
    credentials_path = os.path.join('/Users/sanghoonchung/kivynew/dist/', 'credentials.json')

    if os.path.exists(token_path):# Load credentials from token.pickle if it exists.
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:# If credentials are not valid, refresh or obtain new credentials.
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, ['https://www.googleapis.com/auth/drive'])
            creds = flow.run_local_server(port=0)

        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    return creds



def list_files(service):# Define a function to list CSV files from the Google Drive.
    try:# Query the Google Drive API for files with mimeType 'text/csv' and request 'id' and 'name' fields.
        results = service.files().list(q="mimeType='text/csv'", fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])# Extract the list of files from the API response.

        if not items:# If no files are found, print a message.
            print('No files found.')
        else:# Print the name and ID of each file found.
            print('Files:')
            for item in items:
                print(f"{item['name']} ({item['id']})")

    except HttpError as error:# Handle any exceptions raised during the API request.
        print(f"An error occurred: {error}")
        items = None
    return items# Return the list of files or None if an error occurred.

if __name__ == "__main__":# Entry point for the application.
    MainApp().run()# Run the MainApp.
