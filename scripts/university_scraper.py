from bs4 import BeautifulSoup
import requests
import xlsxwriter

# Here, we're just importing both Beautiful Soup and the Requests library
page_link = 'https://www.studis-online.de/Hochschulen/'
page = 'Seite-'


def lambda_filter(tag):
    if (tag.name == 'div'):
        try:
            # print(tag['class'])
            return tag.name == 'div' and tag['class'] == ['ston-klein', 'ston-mt1']
        except:
            # print('no class')
            return False
    return False

def parse_div_info(item):
    uni_title = item.select_one('b').text
    # print('TITLE ', uni_title)
    uni_info = item.find(lambda_filter)
    uni_limits = uni_info.br.previous_sibling
    # print(uni_limits)
    uni_spec = uni_info.select_one('a.ston-lu').text
    # print(uni_spec)
    return {'title': uni_title, 'limits': uni_limits, 'specialisations': uni_spec}

all_items = []
# this is the url that we've already determined is safe and legal to scrape from.
for nr in range(1,18):
    if(nr == 1):
        page_response = requests.get(page_link, timeout=5)
    else:
        page_response = requests.get(page_link+page+str(nr), timeout=5)

    # here, we fetch the content from the url, using the requests library
    page_content = BeautifulSoup(page_response.content, "html.parser")

    #we use the html parser to parse the url content and store it in a variable.
    items = page_content.find_all("div", class_="ston-hslistdiv")

    all_items += items
    # all_items.append(items)

print(all_items)
unis = []

for item in all_items:

    uni = parse_div_info(item)
    unis.append(uni)

# print(unis)

workbook = xlsxwriter.Workbook('unis.xlsx')
worksheet = workbook.add_worksheet()

row = 0
col = 0
for key in unis[0].keys():
    worksheet.write(row, col, key)
    col += 1

for uni in unis:
    col = 0
    for item in uni.values():
        print(item)
        worksheet.write(row+1, col, item)
        col +=1
    row += 1

workbook.close()