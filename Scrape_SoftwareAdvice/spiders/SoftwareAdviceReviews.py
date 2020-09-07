import scrapy
from scrapy_splash import SplashRequest

class SoftwareAdviceReviewsSpider(scrapy.Spider):
    name = 'SoftwareAdviceReviews'

    allowed_domains = ['softwareadvice.com']

    # lua_script = """
    #     function main(splash, args)
    #     assert (splash:go(args.url))
    #     assert (splash:wait(10))
    #     return {
    #         html = splash:html(),
    #         png = splash:png(),
    #         har = splash:har(),
    #     }
    #     end
    #     """

    # Use a class member to keep track of whether the last search page has been visited
    last_page_counter = 0

    def start_requests(self):
        myBaseUrl = "https://www.softwareadvice.com/bi/dundas-bi-profile/reviews/?review.page="

        start_urls=[]

        for i in range(1, 10):
            start_urls.append(myBaseUrl + str(i))

        for url in start_urls:
            # Use the SplashRequest with a large wait time to cope with the Javasceipt dynamic content of the site
            yield SplashRequest(url, callback=self.parse, args={'wait': 10})

    def parse(self, response):
        # Extract the overall rating based on class name
        overall_rating_map = {'new-stars-rank__100': 5.0, 'new-stars-rank__90': 4.5, 'new-stars-rank__80': 4.0, 'new-stars-rank__70': 3.5, 'new-stars-rank__60': 3.0, 'new-stars-rank__50': 2.5, 'new-stars-rank__40': 2.0, 'new-stars-rank__30': 1.5, 'new-stars-rank__20': 1.0, 'new-stars-rank__10': 0.5, 'new-stars-rank__0': 0.0}

        main_review_block = response.css('.review')

        company_name = response.css('.breadcrumbs').xpath(".//a[@class='small']/text()").extract()[-1].strip()

        review_page_end = response.xpath(".//strong[contains(@data-numberofreviews, 'start')]/following-sibling::strong[1]/text()").extract()
        review_page_total = response.xpath(".//strong[contains(@data-numberofreviews, 'start')]/following-sibling::strong[2]/text()").extract()

        # Skip if the last search page is already visited
        if (review_page_end == review_page_total):
            if self.last_page_counter == 0:
                self.last_page_counter += 1
            else:
                return

        for review in main_review_block:
            # The overall rating is derived from a class name field unlike the rest
            reviewer_overall_rating_element = review.xpath(".//div[contains(@class, 'new-stars-rank')]/@class").extract()
            reviewer_overall_rating = overall_rating_map[reviewer_overall_rating_element[0].split()[-1]]

            reviewer_name = review.xpath(".//strong[@class='review-profile-name']/text()").extract()
            reviewer_company = review.xpath(".//strong[@class='review-profile-company']/text()").extract()

            # Unlike the overall rating, the dimension ratings can be obtained from the text field
            review_dimension = review.xpath(".//p[@class='small']/text()").extract()
            review_dimension_rating = review.xpath(".//div[@class='ranking-pills-number']/p[@class='xsmall strong']/text()").extract()

            review_title = review.xpath(".//p[contains(@class, 'review-copy-header') and contains(@class, 'strong')]/text()").extract()
            review_summary = review.xpath(".//p[contains(@class, 'review-copy-summary') and contains(@class, 'ui')]/text()").extract()
            review_pros = review.xpath(".//p[contains(@data-review, 'pros')]/following-sibling::p[1]/text()").extract()
            review_cons = review.xpath(".//p[contains(@data-review, 'cons')]/following-sibling::p[1]/text()").extract()

            # Generate the output dict object
            yield_dict = {}
            yield_dict['Entry'] = company_name
            if len(reviewer_name) > 0:
                yield_dict['Reviewer'] = reviewer_name[0].strip()
            if len(reviewer_company) > 0:
                yield_dict['Reviewer company'] = reviewer_company[0].strip()
            yield_dict['Overall rating'] = reviewer_overall_rating
            yield_dict.update({dimension: rating for dimension, rating in zip(review_dimension, review_dimension_rating)})
            dimensions = ['Ease-of-use', 'Value for money', 'Customer support', 'Functionality']
            for d in dimensions:
                yield_dict[d] = yield_dict.get(d)
            yield_dict['Review title'] = review_title
            yield_dict['Review summary'] = review_summary
            yield_dict['Review pros'] = review_pros
            yield_dict['Review cons'] = review_cons

            yield yield_dict
