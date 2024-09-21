from chat_bot import ChatBot
from company_data.company import Company

import requests
import numpy as np
import pandas as pd


def download_pdf(url: str, save_path: str):
    response = requests.get(url)

    if response.status_code == 200:
        with open(save_path, "wb") as file:
            file.write(response.content)
        print(f"PDF successfully downloaded and saved to {save_path}")
    else:
        print(f"Failed to download PDF. Status code: {response.status_code}")


def smart_stream(ticker: str):

    company = Company(ticker)
    path = f"{company.base_path}/Book1.xlsx"
    df = pd.read_excel(path)
    ticker = ticker.lower()

    for i, row in df.iterrows():
        url = row["Url"]
        if pd.isna(url):
            pass
        else:
            quarter = row["Period"].lower()
            year = row["Year"]
            file_name = f"{ticker}_sec_{quarter}_{year}.pdf"
            save_path = f"{company.sec_dir}/{file_name}"
            download_pdf(url=url, save_path=save_path)


def smart_download(ticker: str):
    ticker = ticker.lower()
    company = Company(ticker)

    files = {
        # f"{ticker}_sec_q2_2024": "https://s27.q4cdn.com/397450999/files/doc_financials/2024/q2/coin-20240630.pdf",
        # f"{ticker}_sec_q1_2024": "https://s27.q4cdn.com/397450999/files/doc_financials/2024/q1/0dac9418-51fc-43c7-bb60-ee8b65a9bebe.pdf",
        # # ---- 2023
        # f"{ticker}_sec_q4_2023": "https://www.abc.xyz/assets/4b/01/aae7bef55a59851b0a2d983ef18f/596de1b094c32cf0592a08edfe84ae74.pdf",
        # f"{ticker}_sec_q3_2023": "https://s27.q4cdn.com/397450999/files/doc_financials/2023/q3/coin-20230930.pdf",
        # f"{ticker}_sec_q2_2023": "https://s27.q4cdn.com/397450999/files/doc_financials/2023/q2/9dcd01f7-3e99-4ad7-8d9c-fb39e00db165.pdf",
        # f"{ticker}_sec_q1_2023": "https://s27.q4cdn.com/397450999/files/doc_financials/2023/q1/e02f6e36-2945-4ee0-b947-e85b94ebbcd9.pdf",
        # # ---- 2022
        # f"{ticker}_sec_q4_2022": "https://www.abc.xyz/assets/43/22/5deefff4fbec54014ae97b340c22/34ac6dab5f586b2e6e008b99fe683e35.pdf",
        # f"{ticker}_sec_q3_2022": "https://s27.q4cdn.com/397450999/files/doc_financials/2022/q3/a2c76620-9756-4268-9d08-4c7856f25a14.pdf",
        # f"{ticker}_sec_q2_2022": "https://s27.q4cdn.com/397450999/files/doc_financials/2022/q2/304d84bd-3534-4bba-a27c-d1c962a79fc6.pdf",
        # f"{ticker}_sec_q1_2022": "https://s27.q4cdn.com/397450999/files/doc_financials/2022/q1/89c60d81-41a2-4a3c-86fb-b4067ab1016c.pdf",
        # ---- 2021
        f"{ticker}_sec_q4_2021": "https://s27.q4cdn.com/397450999/files/doc_financials/2021/q4/8e5e0508-da75-434d-9505-cba99fa00147.pdf",
        f"{ticker}_sec_q3_2021": "https://s27.q4cdn.com/397450999/files/doc_financials/2021/q3/96565d20-f38b-49e3-a725-0e656b940b09.pdf",
        f"{ticker}_sec_q2_2021": "https://s27.q4cdn.com/397450999/files/doc_financials/2021/q2/dcec079b-3237-4ae0-a54d-479ded972ab8.pdf",
        f"{ticker}_sec_q1_2021": "https://s27.q4cdn.com/397450999/files/doc_financials/2021/q1/cb843fec-ede4-4ff0-be56-a69062543e57.pdf",
    }

    for key, value in files.items():

        save_path = f"{company.sec_dir}/{key}.pdf"
        print(f"Save: {save_path}")
        download_pdf(url=value, save_path=save_path)


from scraper.profiles.amzn import AmznScraper
import time

if __name__ == "__main__":
    ticker = "AMZN"
    c = ChatBot(ticker, use_sec=True)
    c.handle_chat(include_sources=True, use_prep=True)
    # # c = Company(ticker)
    # a = AmznScraper()
    # # a._create_browser(a.url)
    # a.download_pdf_from_csv()
    # # a._scrape(year_limit=2005)
    # # time.sleep(1000)

    # #
    # smart_stream(ticker)
    # smart_download(ticker)
    #
    # c.handle_chat(include_sources=True, use_prep=True)
    # c.visualize_knowledge_graph()
