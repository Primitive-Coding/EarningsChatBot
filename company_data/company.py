import os


class Company:
    def __init__(self, ticker: str) -> None:
        self.ticker = ticker.upper()
        # Base Path
        self.base_path = f"./company_data/tickers/{self.ticker}"
        os.makedirs(self.base_path, exist_ok=True)
        # PDF Folder
        self.pdf_dir = f"{self.base_path}/files"
        os.makedirs(self.pdf_dir, exist_ok=True)
        # Database Path
        self.database_dir = f"{self.base_path}/database"
        self.chroma_path = self.database_dir
        os.makedirs(self.database_dir, exist_ok=True)
        # SEC Files Folder
        self.sec_dir = f"{self.base_path}/sec_files"
        os.makedirs(self.sec_dir, exist_ok=True)
        # SEC Database
        self.sec_db = f"{self.base_path}/sec_database"
        os.makedirs(self.sec_db, exist_ok=True)
