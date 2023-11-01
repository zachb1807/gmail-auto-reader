
# Gmail Auto-Reader
Automatically downloads all the images from the emails in your inbox to make it appear as though you have opened the message. Useful for mass mailing systems with web pixel tracking.


### Getting started
1. Clone this repo to your local filesystem.
2. Install required Python dependancies with pip:
    ```
    pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib requests_futures
    ```
3. Follow the steps to setup the Google API [here](https://developers.google.com/gmail/api/quickstart/python#enable_the_api), until you reach the section titled "Install the Google client library". Save the ```credentials.json``` file in your cloned directory.
4. Open a terminal to your cloned working directory and run ```auto-reader.py```. On the first run, it will open a webpage to authorize using Google OAuth. After, your account token will be stored in a ```token.json``` file in the program directory.
5. Follow the instructions in the program
