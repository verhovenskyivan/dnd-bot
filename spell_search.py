import requests
from bs4 import BeautifulSoup

def parse_spell(spell_name):
    search_url = "https://ttg.club/spells"
    payload = {"search": spell_name}
    
    # Кодирование значений в словаре payload
    encoded_payload = {key: value.encode('utf-8') if isinstance(value, str) else value for key, value in payload.items()}
    
    response = requests.post(search_url, data=encoded_payload)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        spell_link = soup.find('a', class_='search-result-link')
        if spell_link:
            spell_url = "https://ttg.club" + spell_link['href']
            spell_response = requests.get(spell_url)
            if spell_response.status_code == 200:
                spell_soup = BeautifulSoup(spell_response.content, 'html.parser')
                spell_details = spell_soup.find('div', class_='spell-details')
                if spell_details:
                    # Название заклинания
                    print(spell_details.find('h1').text.strip())

                    # Описание заклинания
                    print(spell_details.find('div', class_='spell-description').text.strip())

                    # Другие детали заклинания
                    details = spell_details.find_all('div', class_='spell-detail')
                    for detail in details:
                        key = detail.find(class_='spell-detail-key').text.strip()
                        value = detail.find(class_='spell-detail-value').text.strip()
                        print(f"{key}: {value}")

                else:
                    print("Детали заклинания не найдены.")
            else:
                print("Ошибка при получении данных о заклинании.")
        else:
            print("Заклинание не найдено.")
    else:
        print("Ошибка при получении данных с сайта.")


spell_name = input("Введите название заклинания на русском: ")
parse_spell(spell_name)
