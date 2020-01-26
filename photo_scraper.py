from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from PIL import Image
from io import BytesIO

import requests

driver = webdriver.Chrome()
driver.get("https://google.com")

print(driver.title)
print(driver.current_url)

head_url = "https://creptimg.nims.go.jp/CreptImg/ImageDisp1.cgi?/home/dbmaster/Drawing/fo/ZZ0000"
tail_url = ".FOB%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20"

img_maj = "ABCDEFGH"
img_min = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def login():
	driver.get("https://creptimg.nims.go.jp/CreptImg/ImageFrame.cgi?88&4&3&99&&0&0")
	driver.find_element_by_id("username").send_keys("&&_USERNAME_HERE_&&")
	driver.find_element_by_id("password").send_keys("&&_PASSWORD_HERE_&&")
	driver.find_element_by_id("kc-login").click()
	
def base_url():
	driver.get("https://creptimg.nims.go.jp/CreptImg/ImageFrame.cgi?88&4&3&99&&0&0")

def photo_url(maj, min):
	url = head_url + maj + min + tail_url
	driver.get(url)

def save_img(img_name):
	img = driver.find_element_by_tag_name('img')
	src = img.get_attribute('src')
	print(src)
	
	driver.save_screenshot(img_name)
	
def loop_images():
	for maj_letter in img_maj:
		for min_letter in img_min:
			img_name = "Images/" + maj_letter + min_letter + ".png"
			photo_url(maj_letter, min_letter)
			save_img(img_name)
	
if __name__ == "__main__":
	input("Press Enter To Continue...")
	base_url()
	login()
	loop_images()