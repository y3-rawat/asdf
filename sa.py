import numpy as np
import instaloader 
import os
from pathlib import Path
import shutil
from langchain_groq import ChatGroq
from playwright.sync_api import sync_playwright
import json
import time 
loader = instaloader.Instaloader()
print("-------------------------------------------")
print("Starting")
print("-------------------------------------------")
def prompts(a):
    
    prompt_for_title = f"""
    You are a YouTube caption writer known for crafting strategic, eye-catching titles that maximize audience retention. Your titles excel in optimization and strategy. I will provide a brief video description, and you will generate a captivating title with strategic keywords that maximizes views.

    DESCRIPTION:
    {a}

    INSTRUCTIONS:
    - Provide a title of 100 characters, including keywords for title to make reach of my youtube short .
    - Respond only with the optimized title. No extra commentary.

    """

    prompt_for_keywords =f"""
    You are a YouTube Tags writer known for crafting strategic, tags that maximize Youtube shorts views. Your tags excel in reach and popularity. I will provide a brief video description, and you will generate a captivating tags that maximizes views.
    and also add populer and relevent youtube chennels 
    DESCRIPTION:
    {a}

    INSTRUCTIONS:
    - Provide a tags only of 300 characters.
    - tags should be  saprated by comma.
    - Respond only with the tags Nothing extra.
    EXAMPLE1 OF OUTPUT:

    tag1,tag2,tag3,channel_name1,channel_name2,channel_name3
    REMINDER: Respond only with the optimized tags. No extra commentary.

    """

    prompt_for_description =f"""
    You are a YouTube Description writer known for crafting strategic, tags and content that maximize Youtube shorts views. Your tags excel in reach and popularity. I will provide a brief video description, and you will generate a captivating tags that maximizes views.
    and also add populer and relevent youtube chennels which will help in reach and views.
    DESCRIPTION:
    {a}

    INSTRUCTIONS:
    - Provide a strategic description about the video to maximize views and engagement.
    - tags should be  saprated by comma.
    - Respond only with the description and tags Nothing extra.
    EXAMPLE1 OF OUTPUT:

    this is the discription space 
    ---tags--
    this is the tags space
    tag1,tag2,tag3,channel_name1,channel_name2,channel_name3
    REMINDER: Respond only with the optimized description and tags. No extra commentary.
    2. it should not contrain any thing other then core description and tag

    """
    return prompt_for_title, prompt_for_keywords,prompt_for_description

key = "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"
llm_groq = ChatGroq(groq_api_key=key, model_name="llama3-8b-8192")


path_to_list = os.getcwd()+"\\data_list\\list.txt"
data = []
directory = "Short"
def initalize_stuff():
    with open(path_to_list, 'r') as file:
        existing_list = file.readlines()
    for i in existing_list:
        data.append(i.replace('\n', ''))
    num = np.random.randint(0, len(data)-1)
    print(num)
    code_selected = data.pop(num)
    with open(path_to_list, 'w') as file:
        for code in data:
            file.write(code + '\n')


    """Taking video from code"""

    post = instaloader.Post.from_shortcode(loader.context, code_selected)
    # filePath = r"C:\Users\y3raw\OneDrive\Desktop\vidpath"
    loader.download_post(post, target=directory)
    """Featching content"""
    
    
    existing_files = sorted(os.listdir(directory))
    text_files = [f for f in existing_files if f.endswith('.txt')]
    with open (f"{directory}/{text_files[0]}", "r") as file:
        a  = file.readlines()
    video_path = [f for f in existing_files if f.endswith('.mp4')]

    """Writing content """
    
    
    prompt_for_title, prompt_for_keywords,prompt_for_description = prompts(a)
    final_title = llm_groq.invoke(prompt_for_title).content
    tags = llm_groq.invoke(prompt_for_keywords).content
    description = llm_groq.invoke(prompt_for_description).content
    print("-------------------------------------------")
    print("Post Fetched Successfully")
    print("-------------------------------------------")
    return final_title,description, tags,video_path
pth = os.getcwd()+"\\Short"

def load_cookies_and_visit(final_title,description, tags,video_path):
    with sync_playwright() as p:
        browser =p.firefox.launch()
        context = browser.new_context()
        # Load cookies from file
        with open('cookie/cookies.json', 'r') as f:
            cookies = json.loads(f.read())
            for cookie in cookies:
                context.add_cookies([cookie])

        page = context.new_page()
        page.goto('https://www.youtube.com/',timeout=320000)
        print("-------------------------------------------")
        print("Youtube Page Loaded")
        print("-------------------------------------------")
        time.sleep(2)
        # Your subsequent actions
        page.click('button[aria-label="Create"]')
        page.click('text="Upload video"')
        # page.click("#select-files-button")
        # page.click or page.drag_and_drop as necessary
        page.set_input_files("input[type='file']",f"{pth}/{video_path[0]}")  # Using CSS selector to find the input
        print(video_path)
        time.sleep(2)
        page.locator('div#textbox').nth(0).fill(final_title.replace('"',""))  # First element with id="textbox"
        time.sleep(2)
        page.locator('div#textbox').nth(1).fill(description.replace('"',""))  # Second element with id="textbox"
        # time.sleep(20)
        # page.get_by_text("select").click()
        # page.get_by_text("Best Short Track").click()
        # page.get_by_text("DONE").click()
        time.sleep(1)

        try:
            print("another one ")
            # Locate the custom radio button by its name attribute and click it
            page.locator('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]').click()
        except:
            print("first")
            page.get_by_text("No, it's not 'Made for Kids'").click()
        page.locator('div.label.style-scope.ytcp-button:has-text("Show more")').click()
        
        # Enter each tag followed by an Enter key press
        # input_selector = 'input[placeholder="Add tag"]'
        # for tag in tags:
        #     # Use a more reliable way to select the input based on the placeholder
        #     page.wait_for_selector(input_selector)  # Ensure the input is ready
        #     page.fill(input_selector, tag)  # Fill the input with the tag
        #     page.keyboard.press("Enter")

        time.sleep(3)
        print("-------------------------------------------")
        print("present in tags")
        print("-------------------------------------------")
        try:
            if page.locator('input[placeholder="Add tag"]'):
                print("here----------")
                input_selector = 'input[placeholder="Add tag"]'

                input_element = page.locator(input_selector)
                input_element.wait_for()  # Wait until the input element is ready
                # Fill the input with the tag and press "Enter"
                input_element.type(tags)
                page.keyboard.press("Enter")
                # Optionally wait for the tag to be processed
                time.sleep(2)
                page.click('ytcp-button#next-button')
                page.click('ytcp-button#next-button')
                page.click('ytcp-button#next-button')
                page.click('div#radioLabel')
                time.sleep(3)



                try:
                    
                    page.get_by_text("Public").click()
                    print("1")
                except:
                    try:
                        
                        page.click('tp-yt-paper-radio-button[name="PUBLIC"]')
                        print("2")
                    except:
                        try:
                            
                            page.evaluate('''() => {document.querySelector('tp-yt-paper-radio-button[name="PUBLIC"]').click();}''')
                            print('3')
                        except:
                            print("no one ")
                time.sleep(3)

                page.click('div.label.style-scope.ytcp-button:has-text("Save")')
                

                time.sleep(20)
            else:
                print("here--------else--")    
                page.click('ytcp-button#next-button')
                page.click('ytcp-button#next-button')
                page.click('ytcp-button#next-button')
                page.click('div#radioLabel')
                time.sleep(3)



                try:
                    
                    page.get_by_text("Public").click()
                    print("1")
                except:
                    try:
                        
                        page.click('tp-yt-paper-radio-button[name="PUBLIC"]')
                        print("2")


                    except:
                        try:
                            
                            page.evaluate('''() => {document.querySelector('tp-yt-paper-radio-button[name="PUBLIC"]').click();}''')
                            print('3')
                        except:
                            print("no one ")
                time.sleep(3)
                page.click('div.label.style-scope.ytcp-button:has-text("Save")')
                time.sleep(20)
                print("```````````````````````````````````````````")
                print("-------------------------------------------")
                print("Done")
                print("-------------------------------------------")
                print("```````````````````````````````````````````")
        except:
            
            page.click('ytcp-button#next-button')
            page.click('ytcp-button#next-button')
            page.click('ytcp-button#next-button')
            page.click('div#radioLabel')
            time.sleep(3)



            try:
                
                page.get_by_text("Public").click()
                print("1")
            except:
                try:
                    
                    page.click('tp-yt-paper-radio-button[name="PUBLIC"]')
                    print("2")
                except:
                    try:
                        
                        page.evaluate('''() => {document.querySelector('tp-yt-paper-radio-button[name="PUBLIC"]').click();}''')
                        print('3')
                    except:
                        print("no one ")
            time.sleep(3)
            

            try:  
                print("publish")
                page.click('div.label.style-scope.ytcp-button:has-text("Publish")')
                
            except:
                try:
                    page.click('div.label.style-scope.ytcp-button:has-text("PUBLISH")')
                    print("publish")
                except:
                    print("under except")
                    page.click('div.label.style-scope.ytcp-button:has-text("Save")')


            print("```````````````````````````````````````````")
            print("-------------------------------------------")
            print("Done")
            print("-------------------------------------------")
            print("```````````````````````````````````````````")
            
            



def kick_off():
    print("```````````````````````````````````````````")
    print("-------------------------------------------")
    print("REMOVING PREVIOUS SHORTS")
    print("-------------------------------------------")
    print("```````````````````````````````````````````")
    # Specify the directory to clear
    folder = Path('Short')

    # Check if the folder exists
    if folder.exists() and folder.is_dir():
        # Iterate through all contents and delete them
        for item in folder.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()  # Remove file or symbolic link
                elif item.is_dir():
                    shutil.rmtree(item)  # Remove directory and its contents
            except Exception as e:
                print(f'Failed to delete {item}. Reason: {e}')
    else:
        print(f"The directory '{folder}' does not exist or is not a directory.")




kick_off()
final_title,description, tags,video_path = initalize_stuff()
load_cookies_and_visit(final_title,description, tags,video_path)

# except:
#     print("not able to post video tring again ")