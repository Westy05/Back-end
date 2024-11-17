import requests
import json
from bs4 import BeautifulSoup
import boto3
import tempfile
import time
import os

#the access keys are not being made public to github lol

def s3(ticker, data):
    s3_bucket_name = "investifyhackathon"
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = "us-west-2"

    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )

    # Define the S3 file name based on the ticker
    s3_file_name = f"{ticker}.txt"

    # Write data to a temporary file and upload to S3
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
        temp_file.write(data)
        temp_file_path = temp_file.name

    # Upload the file to S3
    try:
        s3_client.upload_file(temp_file_path, s3_bucket_name, s3_file_name)
        print(f"File successfully uploaded to S3: {s3_bucket_name}/{s3_file_name}")
    except Exception as e:
        print(f"An error occurred: {e}")




def get_10k_text(ticker: str) -> str:
    headers = {
        "User-Agent": "YourEmail@domain.com",
    }
    search_url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={ticker}&owner=exclude&action=getcompany"
    cik_response = requests.get(search_url, headers=headers)
    if cik_response.status_code != 200:
        raise ValueError(f"Failed {ticker}. HTTP Status Code: {cik_response.status_code}")

    cik_start = cik_response.text.find("CIK=") + 4
    cik_end = cik_response.text.find("&", cik_start)
    cik = cik_response.text[cik_start:cik_end].strip().zfill(10)

    submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    submissions_response = requests.get(submissions_url, headers=headers)
    if submissions_response.status_code != 200:
        raise ValueError(f"Failed {cik}. HTTP Status Code {submissions_response.status_code}")

    filings_data = submissions_response.json()
    filings = filings_data.get("filings", {}).get("recent", {})

    form_types = filings.get("form", [])
    accession_numbers = filings.get("accessionNumber", [])
    primary_documents = filings.get("primaryDocument", [])

    recent_10k = None
    for form, acc_num, doc in zip(form_types, accession_numbers, primary_documents):
        if form.upper() == "10-Q":
            recent_10k = {"accession": acc_num, "document": doc}
            break

    if not recent_10k:
        raise ValueError(f"No 10-Q filings found for ticker {ticker}.")

    accession_number = recent_10k["accession"]
    formatted_accession = accession_number.replace("-", "")
    base_url = "https://www.sec.gov/Archives/edgar/data"
    document_url = f"{base_url}/{cik}/{formatted_accession}/{recent_10k['document']}"

    filing_response = requests.get(document_url, headers=headers)
    if filing_response.status_code != 200:
        raise ValueError(f"Failed to fetch the 10-Q document. HTTP Status Code: {filing_response.status_code}")

    soup = BeautifulSoup(filing_response.content, "html.parser")

    filing_text = soup.get_text()

    return filing_text


with open('tickers.json', 'r') as fh:
    data = json.load(fh)

for i in data:
    ticker = data[i]['ticker']
    try:
        text = get_10k_text(ticker)
        s3(ticker, text)
        print(f"Retrieved 10-Q text for {ticker}.")
    except ValueError as e:
        print(e)
        continue
