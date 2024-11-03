# Include libraries
from tkinter import *
from tkinter import ttk,filedialog,messagebox
import base64
import json
from pathlib import Path
from bs4 import BeautifulSoup
import requests

config = {}

# Fetch URL entered by user, then fetch content depending on selected button
def fetch_url(button_id):
    
    # Get user-entered URL from field
    url = _url.get()

    config['images'] = []
    _content.set(())  # initialized as an empty tuple

    # Retrieve data from specified URL, and scrape specified content from it
    try:  # attempt to retrieve data from URL
        
        # Send GET request to URL, and retrieve data from there
        page = requests.get(url)

    except requests.RequestException as err:  # if RequestException arises
        
        # Display exception to status bar
        sb(str(err))

    else:  # occurs if no exception arises
        
        # Retrieve HTML content into BeautfiulSoup object
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Fetch images
        if(button_id == "img"):  # if fetch images button was selected
            
            # Fetch images found within page
            images = fetch_content(soup, url)

            # Display result of image scrape
            if images:  # if there are elements inside list of images
                
                # Set names of images to be displayed in content box
                _content.set(tuple(img['name'] for img in images))

                # Print status message on how many images were found
                sb('Images found: {}'.format(len(images)))

            else:  # if there are not elements inside list of images
                
                # Print status message that no images were found
                sb('No images found')

            # Assign list of images to the 'images' key in the 'config' dictionary    
            config['images'] = images

        # Fetch title
        if(button_id == "title"):  # if fetch title button was selected
            
            # Scrape for title; print it if found, or if none exist print that none exist
            try:  # attempt to scrape title, and return to be printed
                
                # Fetch title
                title = fetch_title(soup)
                
                # Print title result to status bar of application
                if((title != "Error response")):  # if "Err response" was not receieved, meaning URL destination exists

                    # Print scraped title to status bar
                    sb(f"Title found: ['{fetch_title(soup)}']")
                
                else:  # if "Error response" was received, meaning URL destination does not exist
                    
                    # Raise AttributeError exception
                    raise AttributeError("Received error response")

            except AttributeError:  # if AttributeError arises, meaning that no title was found

                # Print to status bar of application that no title was found
                sb("No title found")

        # Fetch URLs
        if(button_id == "urls"):  # if fetch urls button was selected

            # Fetch links found within page
            links = fetch_urls(url)

            # Display result of link scrape
            if links:  # if there are elements inside list of links

                # Set links to be displayed in content box
                _content.set("\n".join(links))  # newline for after each element (link) in list, joined with the data of the list; this combines into one string, as .set() for the StringVar can only take one value

                # Print status message on how many links were found
                sb(f"Links found: {len(links)}")
        
            else:  # if there are no elements inside list of links

                # Print status message that no links were found
                sb("No links found")

# Fetch images within URL
def fetch_content(soup, base_url):
    images = []
    for img in soup.findAll('img'):
        src = img.get('src')
        img_url = f'{base_url}/{src}'
        name = img_url.split('/')[-1]
        images.append(dict(name=name, url=img_url))
    return images

# Fetch title within URL
def fetch_title(soup):

    # Return title of page
    return soup.title.get_text()

# Fetch all external URLs from a webpage, and display in content field
def fetch_urls(url):

    # Making requests instance through GET request, fetch the HTML source
    reqs = requests.get(f'{url}')

    # Declare empty list for links
    linksList = []

    # Parse through HTML and extract links
    soup = BeautifulSoup(reqs.text, 'html.parser')
    links = soup.select('a')  # gather all <a> elements, and returns as a single list

    # Iterate through list of <a> fields within source HTML
    for link in links:

        # If there if href content within <a> field, verify it is an external link, and add to list of links
        if(link.get('href') != None):  # if href field is not empty (contains something)

            # Add link to list if it begins with http:// or https://, and is an external link (meaning the base URL is not part of the site being scraped)
            if(any(protocol in link.get('href') for protocol in ("http://", "https://")) and (url not in link.get('href'))):  # any just means that if for the protocols in the collection of "http://" and "https://", associated with 'protocol', if it is in link.get('href'), then the condition is true (any = or, all = and; same process for both)

                # Add link to list of links
                linksList.append(link.get('href'))
    
    # Return list of links
    return linksList

# Save
def save():
    if not config.get('images'):
        alert('No images to save')
        return

    if _save_method.get() == 'img':
        dirname = filedialog.askdirectory(mustexist=True)
        save_content(dirname)
    else:
        filename = filedialog.asksaveasfilename(
            initialfile='images.json',
            filetypes=[('JSON', '.json')])
        save_json(filename)

# Save images to directory
def save_content(dirname):
    if dirname and config.get('images'):
        for img in config['images']:
            img_data = requests.get(img['url']).content
            filename = Path(dirname).joinpath(img['name'])
            with open(filename, 'wb') as f:
                f.write(img_data)
        alert('Done')

# Save as JSON file
def save_json(filename):
    if filename and config.get('images'):
        data = {}
        for img in config['images']:
            img_data = requests.get(img['url']).content
            b64_img_data = base64.b64encode(img_data)
            str_img_data = b64_img_data.decode('utf-8')
            data[img['name']] = str_img_data

        with open(filename, 'w') as ijson:
            ijson.write(json.dumps(data))
        alert('Done')

# Display message
def sb(msg):
    _status_msg.set(msg)

# Display alert message
def alert(msg):
    messagebox.showinfo(message=msg)

# Execute program
if __name__ == "__main__": # execute logic if run directly

    _root = Tk() # instantiate instance of Tk class
    _root.title("Brady's Web Scraper")
    _mainframe = ttk.Frame(_root, padding='5 5 5 5 ') # root is parent of frame
    _mainframe.grid(row=0, column=0, sticky=("E", "W", "N", "S")) # placed on first row,col of parent
    # frame can extend itself in all cardinal directions
    _url_frame = ttk.LabelFrame(
        _mainframe, text='URL', padding='5 5 5 5') # label frame
    _url_frame.grid(row=0, column=0, sticky=("E","W")) # only expands E W
    _url_frame.columnconfigure(0, weight=1)
    _url_frame.rowconfigure(0, weight=1) # behaves when resizing

    _url = StringVar()
    _url.set('http://localhost:8000') # sets initial value of _url
    _url_entry = ttk.Entry(
        _url_frame, width=40, textvariable=_url) # text box
    _url_entry.grid(row=0, column=0, sticky=(E, W, S, N), padx=5)
    
    # grid mgr places object at position
    # Fetch img button
    _fetch_img_btn = ttk.Button(
        _url_frame, text='Fetch imgs', command=lambda: fetch_url("img")) # create button, fetch_url() is callback for button press, passing in "img" to fetch images
    _fetch_img_btn.grid(row=0, column=1, sticky=W, padx=5, pady=3)

    # Fetch title button
    _fetch_title_btn = ttk.Button(
        _url_frame, text='Fetch title', command=lambda: fetch_url("title")) # create button, fetch_url() is callback for button press, passing in "title" to fetch title
    _fetch_title_btn.grid(row=1, column=1, sticky=W, padx=5, pady=3)

    # Fetch link button
    _fetch_link_btn = ttk.Button(
        _url_frame, text='Fetch links', command=lambda: fetch_url("urls")) # create button, fetch_url() is callback for button press, passing in "urls" to fetch URLs
    _fetch_link_btn.grid(row=2, column=1, sticky=W, padx=5, pady=3)

    # content_frame contains Listbox and Radio Frame
    _content_frame = ttk.LabelFrame(
        _mainframe, text='Content', padding='9 0 0 0')
    _content_frame.grid(row=1, column=0, sticky=(N, S, E, W))

    # Set _content_frame as parent of Listbox and _content is variable tied to
    _content = StringVar()
    _content_listbox = Listbox(
        _content_frame, listvariable=_content, height=6, width=45)
    _content_listbox.grid(row=0, column=0, sticky=(E, W), pady=5)

    # Scrollbar can move vertical
    _scrollbar = ttk.Scrollbar(
        _content_frame, orient=VERTICAL, command=_content_listbox.yview)
    _scrollbar.grid(row=0, column=1, sticky=(S, N), pady=6)
    _content_listbox.configure(yscrollcommand=_scrollbar.set)

    # Listbox occupies (0,0) on _content_frame.
    # Scrollbar occupies (0,1) so _radio_frame goes to (0,2)
    _radio_frame = ttk.Frame(_content_frame)
    _radio_frame.grid(row=0, column=2, sticky=(N, S, W, E))

    # place label and padding
    # radio buttons are children of _radio_frame
    _choice_lbl = ttk.Label(
        _radio_frame, text="Choose how to save images")
    _choice_lbl.grid(row=0, column=0, padx=5, pady=5)
    _save_method = StringVar()
    _save_method.set('img')
    # Radiobutton connected to _save_method variable
    # Know which button is selected by checking value
    _img_only_radio = ttk.Radiobutton(
        _radio_frame, text='As Images', variable=_save_method,
        value='img')
    _img_only_radio.grid(row=1, column=0,padx=5, pady=2, sticky="W")
    _img_only_radio.configure(state='normal')
    _json_radio = ttk.Radiobutton(
        _radio_frame, text='As JSON', variable=_save_method,
        value='json')
    _json_radio.grid(row=2, column=0, padx=5, pady=2, sticky="W")

    # save command saves images to be listed in Listbox after parsing
    _scrape_btn = ttk.Button(
        _mainframe, text='Scrape!', command=save)
    _scrape_btn.grid(row=2, column=0, sticky=E, pady=5)

    _status_frame = ttk.Frame(
        _root, relief='sunken', padding='2 2 2 2')
    _status_frame.grid(row=1, column=0, sticky=("E", "W", "S"))
    _status_msg = StringVar() # need modified when update status text
    _status_msg.set('Type a URL to start scraping')
    _status= ttk.Label(
        _status_frame, textvariable=_status_msg, anchor=W)
    _status.grid(row=0, column=0, sticky=(E, W))

    # Run main program
    _root.mainloop() # listens for events, blocks any code that comes after it