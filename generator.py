import os
import markovify
import requests
import argparse
import codecs

#from reddit.account import Account
from bs4 import BeautifulSoup
#from config import *

url_start = 'http://euw.leagueoflegends.com/en/news/game-updates/patch/patch-'
url_end = '-notes'

#year:highest_patch
patches = {5:24, 6:24, 7:24, 8:24, 9:4}

#relative data directory for storing parsed patches
data_dir = "data"

#relative out directory for storing generated patches
out_dir = "out"

def print_text(text, indentation):
    print((" " * indentation) + text)
    
    
#print with bullet point in front
def print_bullet_point(text, indentation):
    print_text("* " + text, indentation)
    
    
# removes all whitespaces and replaces them with single spaces
def format_text(text):
    return " ".join(text.split())

    
def parse_patch(url):
    summary = ""
    request = requests.get(url)
    
    if request.status_code == requests.codes.ok:   
        soup = BeautifulSoup(request.text, "html.parser")
        container = soup.find("div", {"id": "patch-notes-container"})
        
        if container == None:
            print("Could not find patch-notes-container")
        else:
            summary = get_summary(container)
            changes = get_champ_changes(container)
        
    else:
        print_text("ERROR status_code " + str(request.status_code), 4)
      
    with codecs.open(os.path.join(data_dir, "summaries"), "a", "utf-8") as file:
        file.write(summary + " ")
    
    
def get_summary(container):
    clean_summary = ""
    summary = container.find_next("blockquote", {"class": "blockquote context"})
    
    if summary == None:
        print_bullet_point("No summary found", 4)
    else:
        print_bullet_point("Summary", 4)
        clean_summary = format_text(summary.text)
        
    return clean_summary
    
    
def get_champ_changes(container):
    clean_changes = ''
    champion_header = container.find("h2", {"id": "patch-champions"}).parent
    champion = champion_header.next_sibling
    
    #todo search until next headline because in the champion
    #section there can also be random stuff that can then be
    #filtered out by is_champion (hopefully)
    
    if not is_champion(champion):
        print_bullet_point("No champions found", 4)
    else:
        print_bullet_point("Champions", 4)
        while is_champion(champion):
            name = champion.find("h3", {"class": "change-title"})
            print_bullet_point(format_text(name.text), 6)
            #newline is seperate sibling, skip it
            champion = champion.next_sibling.next_sibling
    
        
def is_champion(content):
    block = content.find("div", {"class": "patch-change-block"})
    return block != None
  
    
def generate_summary(summaries):
    summary = ''
    welcome_model = markovify.Text(summaries, state_size=2)
    summary = welcome_model.make_sentence_with_start('Welcome')
    
    corpus_model = markovify.Text(summaries, state_size=2)
    for i in range(1,20):
        sentence = corpus_model.make_sentence()
        while sentence == None or "Welcome" in sentence:
            sentence = corpus_model.make_sentence()
            
        summary = summary + '\n' + sentence
    
    return summary
  
    
def parse():
    print("cleaning data directory...")
    clean_dir(data_dir)
            
    for year, max_number in patches.items():
        for number in range(1, max_number + 1):
            url = url_start + str(year) + str(number) + url_end
            print_bullet_point(url, 2)
            parse_patch(url)
    
        
def generate():
    summaries = ''
    with codecs.open(os.path.join(data_dir, "summaries"), "r", "utf-8") as file:
        summaries = file.read()
        
    summary = generate_summary(summaries)
    
    with codecs.open(os.path.join(out_dir, "summary"), "w", "utf-8") as file:
        file.write(summary)

        
def clean():
    print_bullet_point("data", 2)
    clean_dir(data_dir)
    print_bullet_point("out", 2)
    clean_dir(out_dir)
    
    
#delete all files in given dir
def clean_dir(dir):
    for file in os.listdir(dir):
        os.unlink(os.path.join(dir, file))
        
        
def main(): 
    parser = argparse.ArgumentParser(description='League of Legends patch notes generator')
    parser.add_argument('-c', '--clean', action="store_true", default=False,
                        dest='clean', help='cleanes data and out directories')
    parser.add_argument('-p', '--parse', action="store_true", default=False,
                        dest='parse', help='parses the patch notes and generates content files')
    parser.add_argument('-g', '--generate', action="store_true", default=False,
                        dest='generate', help='generates patch notes out of content files')
    
    #create needed directories
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    args = parser.parse_args()
    
    if args.clean:
        print("cleaning directories...")
        clean()
    
    if args.parse:
        print("parsing patch notes...")
        parse()
        
    if args.generate:
        print("generating patch notes...")
        generate()
    
    # Check that the config file exists
    #if not os.path.isfile("config.py"):
        #print("config.py not found")
        #print("see config.example.py")
        #exit(1)

    #account = Account(REDDIT_USERNAME, REDDIT_PASSWORD, "PGdevTest 0.1")
    #account.print_stats()

    #account.post_text_submission("test", "this is a test", "text test")
    #submission = account.post_url_submission("test", "this is a test", "http://imgur.com/gallery/eydpv2P")

if __name__ == "__main__":
    main()

