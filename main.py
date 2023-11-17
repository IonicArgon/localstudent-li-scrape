import threading
import time
import json
from playwright.sync_api import sync_playwright

import pprint

# type imports
from playwright.sync_api import Request

username = None
password = None
request_list = []

def intercept_request(request: Request):
    global request_list
    request_list.append(request)

# thread for scraping
def scrape():
    global username
    global password

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        while (username == None or password == None):
            time.sleep(1)

        page.on("request", lambda request: intercept_request(request))

        page.goto("https://www.linkedin.com/login")
        page.fill("#username", username)
        page.fill("#password", password)
        page.click("button[type='submit']")

        if "checkpoint" in page.url and page.get_by_text("Let's do a quick security check").is_visible():
            print("Please complete the security check on the browser and then press enter here.")
            input()
        elif "checkpoint" in page.url and page.get_by_text("Enter"):
            print("Enter the 2FA code here:")
            code = input()
            page.fill("id*=verification_pin", code)
            page.click("button[type='submit']")

        # now navigate to test profile and send a connection request so we can 
        # intercept the request

        page.goto("https://www.linkedin.com/in/emil-sinclair-762636297/")
        
        # there's gonna be two buttons with the same aria label, click both
        print("Click the connect button on the profile and then press enter here.")
        input()

        # sleep a little bit to make sure the request is intercepted
        time.sleep(15)

        # now clean up browser stuff
        page.close()
        browser.close()

if __name__ == "__main__":
    scrape_thread = threading.Thread(target=scrape)
    scrape_thread.daemon = True
    scrape_thread.start()

    print("Enter your LinkedIn username:")
    username = input()
    print("Enter your LinkedIn password:")
    password = input()

    scrape_thread.join()
    
    # search through the list and look for a request to 
    # VoyagerRelationshipsDashMemberRelationships

    main_request: Request = None
    for request in request_list:
        if "VoyagerRelationshipsDashMemberRelationships" in request.url:
            main_request = request
            break

    if main_request == None:
        print("Could not find the request.")
        exit(1)

    # pretty print the request headers
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(main_request.all_headers())
