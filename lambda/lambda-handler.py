## Importing Necessary Modules
import requests # to get image from the web
import shutil # to save it locally
import os
from datetime import datetime
from dateutil import tz
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bom_plots = [
    ("Bega River at Bega North", "http://www.bom.gov.au/fwo/IDN60234/IDN60234.069120"),
    ("Bega River at Kanoona", "http://www.bom.gov.au/fwo/IDN60234/IDN60234.569028"),
    ("Tantawangalo Creek at Candelo Damsite", "http://www.bom.gov.au/fwo/IDN60234/IDN60234.569021"),
    ("Bemboka River at Morans Crossing", "http://www.bom.gov.au/fwo/IDN60234/IDN60234.569013"),
    ("Brogo River at Angledale", "http://www.bom.gov.au/fwo/IDN60234/IDN60234.569008"),
    ("Double Creek near Brogo", "http://www.bom.gov.au/fwo/IDN60234/IDN60234.569027"),
    ("Brogo River at North Brogo", "http://www.bom.gov.au/fwo/IDN60234/IDN60234.569023"),
    ("Brogo Dam", "http://www.bom.gov.au/fwo/IDN60234/IDN60234.569016"),
    ("Pambula River at Lochiel", "http://www.bom.gov.au/fwo/IDN60234/IDN60234.569014")
]

S3_BUCKET_ARN = os.getenv('s3_bucket_arn', 'arn:aws:s3:::begariver-plots-001')
S3_BUCKET_NAME = os.getenv('s3_bucket_name', 'begariver-plots-001')


def download_file(filename, url):

        logger.info("Downloading: "+url)
        logger.info("Writing to: "+filename)

        # Open the url, set stream to True, this will return the stream content.
        r = requests.get(url, stream = True, headers = {'User-Agent': 'Mozilla/5.0'})

        # Check if the image was retrieved successfully
        if r.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            r.raw.decode_content = True
            
            # Open a local file with wb ( write binary ) permission.
            os.chdir('/tmp')
            with open("tempfile",'wb') as f:
                shutil.copyfileobj(r.raw, f)
            
            # now copy the file to s3
            s3_client = boto3.client('s3')
            try:
                response = s3_client.upload_file("tempfile", S3_BUCKET_NAME, filename)
            except ClientError as e:
                logger.error(e)

            logger.info('SUCCESS: File Downloaded, '+ filename)
        else:
            logger.error('ERROR: File Couldn\'t be retrieved: '+ url)


def handler(event, context):

    # make new daily directory
    sydney_tz = tz.gettz("Australia/Sydney")
    now = datetime.now(tz=sydney_tz)
    dirname = now.strftime('%Y/%m/%d')

    # iterate over all river plots and download image and table html
    for idx, (title, image_url) in enumerate(bom_plots):

        filename = dirname+"/"+title
        ## Download the image
        download_file(filename+".png", image_url+".png")

        ## Download the html file
        download_file(filename+".html", image_url+".tbl.shtml")


