import argparse
import json
import itertools
import re
import os
import uuid
import sys
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import logging

REQUEST_HEADER = {
    'User-Agent': "Chrome/43.0.2357.134"}

def get_soup(url, header):
    res = urlopen(Request(url, headers=header))
    return BeautifulSoup(res, 'html.parser')

def qur_url(qur):
    return "https://www.google.co.in/search?q=%s&source=lnms&tbm=isch" % qur

def soup_img(soup):
    img_ele = soup.find_all("div", {"class": "rg_meta"})
    metadata_dicts = (json.loads(e.text) for e in img_ele)
    link_typ = ((d["ou"], d["ity"]) for d in metadata_dicts)
    return link_typ

def imgs(qur, num_img):
    url = qur_url(qur)
    logger.info("Souping")
    soup = get_soup(url, REQUEST_HEADER)
    logger.info("Extracting image urls")
    link_typ = soup_img(soup)
    return itertools.islice(link_typ, num_img)

def get_raw_img(url):
    req = Request(url, headers=REQUEST_HEADER)
    resp = urlopen(req)
    return resp.read()

def save_image(raw_img, img_ty, save_dir):
    ext = img_ty if img_ty else 'jpg'
    file_name = uuid.uuid4().hex + "." + ext
    save_path = os.path.join(save_dir, file_name)
    with open(save_path, 'wb') as image_file:
        image_file.write(raw_img)

def download_images_to_dir(images, save_dir, num_img):
    for i, (url, img_ty) in enumerate(images):
        try:
            logger.info("Making request (%d/%d): %s", i, num_img, url)
            raw_img = get_raw_img(url)
            save_image(raw_img, img_ty, save_dir)
        except Exception as e:
            logger.exception(e)

def run(qur, save_dir, num_img=100):
    qur = '+'.join(qur.split())
    logger.info("Extracting image links")
    images = imgs(qur, num_img)
    logger.info("Downloading images")
    download_images_to_dir(images, save_dir, num_img)
    logger.info("Finished")

def main():
    parser = argparse.ArgumentParser(description='Scrape Google images')
    parser.add_argument('-s', '--search', default='peace', type=str, help='search term')
    parser.add_argument('-n', '--num_img', default=5, type=int, help='num images to save')
    parser.add_argument('-d', '--directory', default='E:\img', type=str, help='save directory')
    args = parser.parse_args()
    run(args.search, args.directory, args.num_img)

if __name__ == '__main__':
    main()
