# ScrapeSoftwareAdviceReviews
A scraper based on scrapy and splash to scrape customer review data for softwareadvice.com.

First, start docker by

```console
docker run -p 8050:8050 scrapinghub/splash
```

Then, run scrapy with

```console
scrapy runspider spiders/SoftwareAdviceReviews.py -o output.csv
```

This will scrape all the reviews from the myBaseUrl URL defined in the main program and store them in the output.csv file.
