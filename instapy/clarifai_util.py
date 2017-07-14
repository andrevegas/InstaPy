"""Module which handles the clarifai api and checks
the image for invalid content"""
from clarifai.rest import ClarifaiApp
from selenium.common.exceptions import NoSuchElementException


def check_image(browser, clarifai_id, clarifai_secret, img_tags, full_match=False):
    """Uses the link to the image to check for invalid content in the image"""
    clarifai_app = ClarifaiApp(clarifai_id, clarifai_secret)
    model = clarifai_app.models.get('general-v1.3')

    img_link = get_imagelink(browser)
    result = model.predict_by_url(img_link)

    clarifai_tags = result['outputs'][0]['data']['concepts']

    for (tags, should_comment, comments) in img_tags:
        if should_comment:
            if given_tags_in_result_list(tags, clarifai_tags, full_match):
                return True, comments
        else:
            if given_tags_in_result_list(tags, clarifai_tags, full_match):
                print('Inappropriate content in Image, not commenting')
                return False, []

    return True, []


def given_tags_in_result_list(search_tags, clarifai_tags, full_match=False):
    for tag in clarifai_tags:
        if tag['value'] > 0.90:
            return given_tags_in_result(search_tags, tag['name'], full_match)
        else:
            return False


def given_tags_in_result(search_tags, clarifai_tags, full_match=False):
    """Checks the clarifai tags if it contains one (or all) search tags """
    if full_match:
        return all([tag in clarifai_tags for tag in search_tags])
    else:
        return any((tag in clarifai_tags for tag in search_tags))


def get_imagelink(browser):
    """Gets the imagelink from the given webpage open in the browser"""
    try:
        return browser.find_element_by_xpath('//img[@class = "_icyx7"]') \
            .get_attribute('src')
    except NoSuchElementException as err:
        return browser.find_element_by_xpath('//video[@class = "_c8hkj"]') \
            .get_attribute('poster')

