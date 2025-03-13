import time

import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_html_content(url, headers):
    """Fetches HTML content from a URL."""
    print("Connecting..")
    response_page = requests.get(url, headers=headers)

    if response_page.status_code == 200:
        print("Connected Successfully")
        return response_page.text
    else:
        print("Connection not successful!")
        return None


def parse_hotel_listings(html_content):
    """Parses hotel listings from HTML content."""
    parsed_page = BeautifulSoup(html_content, 'html.parser')
    return parsed_page.find_all('div', class_="listing-hotels")


def extract_hotel_data(listing):
    """Extracts hotel data from a listing element."""
    try:
        hotel_name = listing.find('h2',
                                  class_="listing-hotels-name").text
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
            rating = "Not Available"
            index = "No Index"
        else:
            rating = rated.text.split(' - ')[0]
            index = rated.text.split(' - ')[1]
        facility = listing.find('div', class_='listing-hotels-facilities d-none d-md-flex')
        if facility is None:
            all_facilities = "No facilities recorded"
        else:
            all_facilities = facility.find_all()
            all_facilities = [fac.find('p').text for fac in all_facilities if fac.find('p') is not None]
            all_facilities = ", ".join(all_facilities)
        likes = listing.find('div', class_='listing-hotels-likes').text
        likes = likes.strip().split()[0]

        return {
            'hotel_name': hotel_name,
            'hotel_address': address,
            'city': city,
            'state': state,
            'price_per_night': price,
            'rating_score': rating,
            'rating_index': index,
            'facilities': all_facilities,
            'popularity': likes
        }
    except AttributeError:
        print("Error processing a hotel listing. Skipping.")
        return None


def get_next_page_url(html_content):
    """Extracts the URL of the next page from the pagination."""
    parsed_page = BeautifulSoup(html_content, 'html.parser')
    next_button = (parsed_page.find('ul', class_='pagination').
                   find('li', class_='placeholders nextBtn'))
    if next_button:
        return next_button.find('a')['href']
    else:
        return None


def main(): 
    """Main function to orchestrate the scraping process."""
    base_url = "https://hotels.ng/hotels-in-abia"
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}

    all_hotels_listing = []  # Temporary Storage
    current_url = base_url

    while current_url:
        html_content = get_html_content(current_url, header)
        if html_content:
            hotel_listings = parse_hotel_listings(html_content)
            for listing in hotel_listings:
                hotel_data = extract_hotel_data(listing)
                if hotel_data:
                    all_hotels_listing.append(hotel_data)

            # Get the next page URL
            next_page_url = get_next_page_url(html_content)
            if next_page_url:
                current_url = next_page_url
                print(f"Scraping next page: {current_url[-1]}")
                time.sleep(2)  # Add a delay before scraping the next page
            else:
                current_url = None  # Stop scraping if there's no next page
        else:
            break  # Stop scraping if there's an error fetching the page

    hotel_df = pd.DataFrame(all_hotels_listing)
    hotel_df.to_csv("hotels.csv", index=False)


if __name__ == "__main__":
    main()