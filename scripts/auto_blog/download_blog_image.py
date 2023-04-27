# This script is used to download images from a selection of free image websites
# the images will match the blog title and be saved in the assets/images folder

import glob
import logging
import os
import requests
import shutil
import time
import yaml
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("download_blog_image.log"), logging.StreamHandler()],
)

# Set the image download folder
IMAGE_DOWNLOAD_FOLDER = "assets/images"


def download_unsplash_image(query, access_key):
    url = f"https://api.unsplash.com/search/photos?query={query}&client_id={access_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            image_url = data["results"][0]["urls"]["regular"]
            image_data = requests.get(image_url).content

            file_name = f"{IMAGE_DOWNLOAD_FOLDER}/{query}.jpg"
            with open(file_name, "wb") as f:
                f.write(image_data)
                print(f"Image '{file_name}' downloaded.")
                return file_name
        else:
            print("No image found for the given query.")
            return None
    else:
        print(f"Error: {response.status_code}")
        return None


def update_blog_page(blog_file, image_file):
    with open(blog_file, "r") as f:
        content = f.read()

    front_matter, post_content = content.split("---", 2)[1:]
    front_matter = front_matter.strip()
    yaml_data = yaml.safe_load(front_matter)

    yaml_data["image"] = image_file

    updated_front_matter = yaml.safe_dump(yaml_data)

    with open(blog_file, "w") as f:
        f.write(f"---\n{updated_front_matter}---{post_content}")

    print(f"Updated blog page '{blog_file}' with image '{image_file}'.")


def get_categories_from_blog(blog_file):
    with open(blog_file, "r") as f:
        content = f.read()

    # logging.info(f"Content {content}")
    front_matter = content.split("---", 2)[1]
    logging.info(f"Front Matter {front_matter}")
    front_matter = front_matter.strip()
    yaml_data = yaml.safe_load(front_matter)
    categories = yaml_data.get("categories", "")
    parsed_categories = categories.split()
    return parsed_categories


def get_latest_blog_file(posts_folder):
    all_files = glob.glob(f"{posts_folder}/*.md")
    return max(all_files, key=os.path.getmtime)


def update_blog_with_downloaded_image(blog_page):
    categories = get_categories_from_blog(latest_blog_page)
    logging.info(f"Categories {categories}")
    if categories:
        search_query = categories[0]
        logging.info(f"Running Image Download For Category {search_query}")
        unsplash_api_key = os.getenv("UNSPLASH_ACCESS_KEY")
        downloaded_image = download_unsplash_image(search_query, unsplash_api_key)
        if downloaded_image:
            logging.info(f"Downloaded Image {downloaded_image}")
            update_blog_page(blog_page, downloaded_image)
    else:
        print("No categories found in the blog page.")


if __name__ == "__main__":
    posts_folder = "_posts"

    latest_blog_page = get_latest_blog_file(posts_folder)
    logging.info(f"Latest Blog Page {latest_blog_page}")

    update_blog_with_downloaded_image(latest_blog_page)
