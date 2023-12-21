import requests
from bs4 import BeautifulSoup
import json
import time

def main():
    url = "https://www.bbcnewsd73hkzno2ini43t4gblxvycyac5aw4gnv7t2rccijh7745uqd.onion/news/entertainment-arts-67726767"
    session = get_tor_session()

    start_time = time.time()
    check_active_link(url, session)
    end_time = time.time()

    print(f"Scraping and saving took {end_time - start_time:.2f} seconds.")

def check_active_link(url, session):
    response = process_check_link(url, session)
    if response["status"] == 200:
        soup = BeautifulSoup(response["response"], 'lxml')
        process_scrapping(soup)
    else:
        print("The link is not active.")

def process_scrapping(soup):
    title = soup.find('h1', class_='ssrcss-15xko80-StyledHeading e10rt3ze0').text
    contents = [content.text.replace("\"", "") for content in soup.find_all('p', class_='ssrcss-1q0x1qg-Paragraph e1jhz7w10')]
    images = [image['src'] for image in soup.find_all('img', class_='ssrcss-evoj7m-Image edrdn950', limit=4)]
    reporter = soup.find('div', class_= 'ssrcss-68pt20-Text-TextContributorName e8mq1e96').text.replace("By ", "")
    link_on_webs = [link['href'] for link in soup.find_all('a', class_= 'ssrcss-k17ofw-InlineLink e1kn3p7n0')] 

    data = {
        "title": title,
        "reporter": reporter,
        "contents": contents,
        "images": images,
        "link_on_web_page": link_on_webs
    }
    save_to_file_json(data, "output.json")

def save_to_file_json(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

def process_check_link(url, session):
    try:
        headers = {"User-Agent": user_agent()}
        response = session.get(url, headers=headers)
        return {
            "status": response.status_code,
            "response": response.text
        }
    except requests.ConnectionError:
        return False

def user_agent():
    return "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"

def get_tor_session():
    session = requests.session()
    session.proxies = {'http': 'socks5h://127.0.0.1:9150',
                       'https': 'socks5h://127.0.0.1:9150'}
    return session

if __name__ == '__main__':
    main()