
# Gmail Auto-Reader
Automatically downloads all the images from the emails in your inbox to make it appear as though you have opened the message. Useful for mass mailing systems with web pixel tracking.


### Getting started
1. Clone this repo to your local filesystem.
2. Install required Python dependancies with pip:
    ```
    pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib requests_futures
    ```
3. Follow the steps to setup the Google API [here](https://developers.google.com/gmail/api/quickstart/python#enable_the_api), until you reach the section titled "Install the Google client library". Ensure you add the email address you would like to use for the Gmail Auto Reader to the "Test Users" in the App Registration settings. Save your ```credentials.json``` file in your cloned directory.
4. In your Gmail inbox, create a label you would like applied to all emails processed by the Auto Reader. For more info on this visit the [Google help page](https://support.google.com/mail/answer/118708?hl=en&co=GENIE.Platform%3DDesktop). Make note of the label's name.
5. Open a terminal to your cloned working directory and run ```labels.py```. On the first run, it will open a webpage to authorize using Google OAuth. Click "Continue" if you're told the app hasn't been verified. Once complete, your account token will be stored in a ```token.json``` file in the program directory.
6. Return to the terminal, and search for the label name you created in Step 4. Copy the label ID displayed to the right (don't include the braces). Store this label ID in a file called ```label_id``` in your working directory.

7. In the same terminal, run ```auto-reader.py``` and follow the instructions in the program.
