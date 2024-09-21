import os
import time
from scraper.scraper import Scraper

import pandas as pd


class AmznScraper(Scraper):
    def __init__(self) -> None:
        self.url = "https://ir.aboutamazon.com/sec-filings/default.aspx"
        self.path = "./company_data/tickers/AMZN/urls.csv"
        super().__init__()

    def _scrape(self, year_limit: int = 2010):

        button_path = "/html/body/div/div/div/form/div[2]/div/div[3]/div[2]/div[2]/div/div/span/span[2]/div/div/div/div[1]/div/div[1]/select"
        qtr_filings_path = "/html/body/div/div/div/form/div[2]/div/div[3]/div[2]/div[2]/div/div/span/span[2]/div/div/div/div[1]/div/div[1]/select/option[3]"
        filing_year_path = "/html/body/div/div/div/form/div[2]/div/div[3]/div[2]/div[2]/div/div/span/span[2]/div/div/div/div[1]/div/div[2]/select"
        pdf_path1 = "/html/body/div/div/div/form/div[2]/div/div[3]/div[2]/div[2]/div/div/span/span[2]/div/div/div/table/tbody/tr[1]/td[4]/ul/li[1]/a"
        pdf_path2 = "/html/body/div/div/div/form/div[2]/div/div[3]/div[2]/div[2]/div/div/span/span[2]/div/div/div/table/tbody/tr[2]/td[4]/ul/li[1]/a"
        pdf_path3 = "/html/body/div/div/div/form/div[2]/div/div[3]/div[2]/div[2]/div/div/span/span[2]/div/div/div/table/tbody/tr[3]/td[4]/ul/li[1]/a"
        option1 = "/html/body/div/div/div/form/div[2]/div/div[3]/div[2]/div[2]/div/div/span/span[2]/div/div/div/div[1]/div/div[2]/select/option[1]"
        option2 = "/html/body/div/div/div/form/div[2]/div/div[3]/div[2]/div[2]/div/div/span/span[2]/div/div/div/div[1]/div/div[2]/select/option[2]"
        options_path = "/html/body/div/div/div/form/div[2]/div/div[3]/div[2]/div[2]/div/div/span/span[2]/div/div/div/div[1]/div/div[2]/select/option[{}]"
        options_index = 1
        self._click_button(button_path, wait=True)
        time.sleep(3)
        self._click_button(qtr_filings_path, wait=True)
        time.sleep(3)

        filings = {}
        while True:
            try:
                link1 = self.get_element_link(pdf_path1)
                link2 = self.get_element_link(pdf_path2)
                link3 = self.get_element_link(pdf_path3)
                filing_year = self._read_data(options_path.format(options_index))

                if int(filing_year) == year_limit:
                    break

                # filing_year = self._read_data(filing_year_path, wait=True)
                # print(f"Filing: {filing_year}")

                if link3 == None and link2 == None:
                    data = {"Q1": link1, "Q2": "", "Q3": ""}
                elif link3 == None:
                    data = {"Q1": link2, "Q2": link1, "Q3": ""}
                else:
                    data = {"Q1": link3, "Q2": link2, "Q3": link1}

                filings[filing_year] = data
                options_index += 1

                print(f"Filings: {filings}")
                time.sleep(3)
                self._click_button(options_path.format(options_index))
            except Exception as e:
                print(f"E: {e}")
                break

            except KeyboardInterrupt:
                break

        years = []
        periods = []
        paths = []
        urls = []

        for k1, v1 in filings.items():
            for k2, v2 in v1.items():
                year = k1
                period = k2.lower()
                path = f"amzn_sec_{period}_{year}.pdf"

                years.append(year)
                periods.append(period)
                paths.append(path)
                urls.append(v2)

        df = pd.DataFrame(
            {"years": years, "periods": periods, "paths": paths, "urls": urls}
        )
        df.to_csv(self.path)

    def download_pdf_from_csv(self):
        df = pd.read_csv(self.path).drop("Unnamed: 0", axis=1)

        existing_files = os.listdir("./company_data/tickers/AMZN/sec_files")

        for i, row in df.iterrows():
            print(f"Row: {row}")

            save_path = f"./company_data/tickers/AMZN/sec_files/{row['paths']}"
            url = row["urls"]

            if row["paths"] in existing_files:
                pass
            else:
                if pd.isna(url):
                    pass
                else:
                    self.download_pdf(url, save_path=save_path)
