import requests # make request to retrieve the page
from bs4 import BeautifulSoup # beautiful soup serves as html parser
import pandas as pd # Pandas providing data maipulation

BASE_URL = "https://hotels.ng/hotels-in-abia"
HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36q (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}

print("Connecting..")
response_page = requests.get(BASE_URL, headers=HEADER, timeout=20)

if response_page.status_code == 200:
    print("Connection Successful")
else:
    print("Connection not successful!")

# parse the html page...
parsed_page = BeautifulSoup(response_page.text, 'html.parser')
# Extracting all hotel listing
hotel_listing = parsed_page.find_all('div', class_="listing-hotels")

# Scraping and transformation of the unstructured data
all_hotels_listing = []
for listing in hotel_listing:
    hotel_name = listing.find('h2', class_="listing-hotels-name").text
    hotel_address = listing.find('p',
                                 class_='listing-hotels-address color-dark').text.strip().split()
    hotel_address = " ".join(hotel_address).split(' - ')
    address = hotel_address[1]
    city = hotel_address[0].split(',')[0]
    state = hotel_address[0].split(',')[1].strip()
    price = listing.find('p', class_='listing-hotels-prices-discount').text
    price = price.strip().split()[0].replace('₦', '').replace(',', '')
    rated = listing.find('p', class_='listing-hotels-rating')
    if rated is None:
        RATING = "Not Available"
        INDEX = "No Index"
    else:
        RATING = rated.text.split(' - ')[0]
        INDEX = rated.text.split(' - ')[1]
    facility = listing.find('div',
                            class_='listing-hotels-facilities d-none d-md-flex')
    if facility is None:
        ALL_FACILITIES = "No facilities recorded"
    else:
        ALL_FACILITIES = facility.find_all()
        ALL_FACILITIES = [fac.find('p').text for fac in ALL_FACILITIES if fac.find('p') is not None]
        ALL_FACILITIES = ", ".join(ALL_FACILITIES)
    likes = listing.find('div', class_='listing-hotels-likes').text
    likes = likes.strip().split()[0]

    # Transformed data to temporary dictionary storage
    hotels_listing = {
        'hotel_name': hotel_name,
        'hotel_address': address,
        'city': city,
        'state': state,
        'price_per_night': price,
        'rating_score': RATING,
        'rating_index': INDEX,
        'facilities': ALL_FACILITIES,
        'popularity': likes
    }
    all_hotels_listing.append(hotels_listing)

hotel_df = pd.DataFrame(all_hotels_listing)  # Convert to dataframe
hotel_df.to_csv("hotels.csv")  # save to csv
