from selenium import webdriver
import selenium
from pprint import pprint
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from configparser import ConfigParser
from pydantic import BaseModel
import logging

logging.basicConfig(
    format="%(asctime)s - %(funcName)s -  %(levelname)s => %(message)s",
    level=logging.INFO,
    handlers=[
        logging.handlers.RotatingFileHandler(
            filename="../logs/worker.log", mode="a", maxBytes=1000000, backupCount=5
        )
    ]
)

config = ConfigParser()
config.read("../.config.ini")

link = config["worker"]["link"]


class AddressDetails(BaseModel):
    street_name: str
    region: str
    district: str
    area: str
    post_code: str
    universal_address: str
    longitude: float
    latitude: float


class GhanaPostGPS:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")

        # Create a new instance of the Chrome driver
        self.driver = webdriver.Chrome(options=chrome_options)

        # Now you can use the driver to interact with web pages
        self.driver.get(str(link))

    def gps_to_loc(self, value: str):
        """Get the location details of the given GPS Address

        Args:
            value (_str_): The GPS Address whose details are to be found.

        Returns:
            _dict_: {
                        "street_name": "string",
                        "region": "string",
                        "district": "string",
                        "area": "string",
                        "post_code": "string",
                        "universal_address": "string",
                        "longitude": 0,
                        "latitude": 0
                    }
        """
        try:
            self.driver.switch_to.alert.accept()  # Switch to focus to the alert on the page and subsequently accept it.
            # GS-0757-3391   VH-0044-1959  GS-0158-0976  GW-0545-2757
            input_ = self.driver.find_element(
                By.XPATH,
                value="/html/body/div[1]/div[1]/div[2]/div[1]/div/div/div[1]/div/input",
            ).send_keys(value, Keys.ENTER)

            time.sleep(5)

            side_bar = self.driver.find_element(by="id", value="side-bar")

            a = side_bar.find_elements(By.CLASS_NAME, "address-list")
            res = a[0].get_attribute("outerHTML")

            html = BeautifulSoup(res, "html.parser")

            ress = html.find_all("div", {"class": "text-warning"})

            try:
                long, lat = eval(ress[6].text)
                result = dict(
                    street_name=ress[0].text,
                    region=ress[1].text,
                    district=ress[2].text,
                    area=ress[3].text,
                    post_code=ress[4].text,
                    universal_address=ress[5].text,
                    # long_lat=ress[6].text
                    longitude=long,
                    latitude=lat,
                )

                self.driver.close()  # Close browser window.
                self.driver.quit()  # End webdriver session.

                final = AddressDetails(**result)
                logging.info(f"Retrieved details for {value}: {final.model_dump()}")
                return final.model_dump()
            except Exception as err:
                logging.error(f"Unable to process address: {err}")

        except selenium.common.exceptions.UnexpectedAlertPresentException as err:
            logging.error(err)
            self.driver.switch_to.alert.accept()


# if __name__ == "__main__":
#     m = GhanaPostGPS()
#     print(m.gps_to_loc("GW-0545-2757"))
