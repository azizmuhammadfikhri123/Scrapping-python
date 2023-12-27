import requests
import json
import time
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic

BOOTSTRAP_SERVER = 'localhost:9092'
CLIENT_ID        = 'python-producer'
TOPIC            = 'scrapping_1'

def main():
    url = "https://www.bbcnewsd73hkzno2ini43t4gblxvycyac5aw4gnv7t2rccijh7745uqd.onion/news"
    session = get_tor_session()

    start_time = time.time()
    check_active_link(url, session)
    end_time = time.time()

    print(f"Scraping and saving took {end_time - start_time:.2f} seconds.")

def check_active_link(url, session):
    response = process_check_link(url, session)
    if response["status"] == 200:
        soup = BeautifulSoup(response["response"], 'lxml')
        process_get_link(soup, url, session)
    else:
        print("The base url is not active.")

def process_get_link(soup, base_url, session):
    links = []
    sites = soup.find_all('a',  class_= 'gs-c-promo-heading gs-o-faux-block-link__overlay-link gel-pica-bold nw-o-link-split__anchor')
    for link in sites[0:10]:
        path = link['href']
        full_url = urljoin(base_url, path)
        links.append(full_url)
    
    process_scrapping(links, session)
    
def process_scrapping(links, session):
    producer = config_kafka()
    data = load_existing_data("output_multi.json")
    check_topic()
    
    for link in links:
        if any(entry['url'] == link for entry in data):
            print(f"Skipping duplicate link: {link}")
            continue
        
        response = process_check_link(link, session)
        if response["status"] == 200:
            soup = BeautifulSoup(response["response"], "lxml")
            
            title_element = soup.find('h1', class_='ssrcss-nsdtmh-StyledHeading e10rt3ze0')
            if not title_element:
                title_element = soup.find('h1', class_='ssrcss-15xko80-StyledHeading e10rt3ze0')
            title = title_element.text if title_element else ""
           
            paragraph_elements = soup.find_all('p', class_='ssrcss-1q0x1qg-Paragraph e1jhz7w10')
            contents = [content.text.replace("\"", "") for content in paragraph_elements] if paragraph_elements else []

            image_elements = soup.find_all('img', class_='ssrcss-evoj7m-Image edrdn950', limit=4)
            images = [image['src'] for image in image_elements] if image_elements else []

            link_elements = soup.find_all('a', class_='ssrcss-k17ofw-InlineLink e1kn3p7n0')
            link_on_webs = [link['href'] for link in link_elements] if link_elements else []
            
            result = {
                "url": link,
                "title": title,
                "contents": contents,
                "images": images,
                "link_on_web_page": link_on_webs
            }
            
            data.append(result)
            send_to_kafka(producer, result)
        else:
            print("The base path is not active.")

    save_to_file_json(data, "output_multi.json")  
    
def load_existing_data(file_path):
    existing_data = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    return existing_data

def check_topic():
    admin_client = AdminClient({'bootstrap.servers': BOOTSTRAP_SERVER})
    topics_metadata = admin_client.list_topics(timeout=5).topics
    
    if TOPIC not in topics_metadata:
        new_topic = NewTopic(TOPIC, num_partitions=1, replication_factor=1)
        admin_client.create_topics([new_topic])
        admin_client.poll(timeout=5)
        print(f'Topic {TOPIC} created.')
    else:
        pass
        
def send_to_kafka(producer, data):
    message_value = json.dumps(data)
    producer.produce(TOPIC, value=message_value, callback=delivery_report)
    producer.flush()

def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))
        
def config_kafka():
    conf = {
        'bootstrap.servers': BOOTSTRAP_SERVER,
        'client.id': CLIENT_ID
    }
    producer = Producer(conf)
    return producer

def save_to_file_json(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

def process_check_link(url, session):
    try:
        headers = {"User-Agent": user_agent()}
        response = session.get(url, headers=headers, timeout=20)
        return {
            "status": response.status_code,
            "response": response.text
        }
    except requests.exceptions.ReadTimeout:
        return {
            "status" : 408,
            "response": "Timeout"
        }
    except requests.ConnectionError:
        return {
            "status": 599,
            "response": "Connection Error"
        }
   

def user_agent():
    return "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def get_tor_session():
    session = requests.session()
    session.proxies = {'http': 'socks5h://127.0.0.1:9150',
                       'https': 'socks5h://127.0.0.1:9150'}
    return session

if __name__ == '__main__':
    main()