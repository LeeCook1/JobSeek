import locale

from urllib.parse import urlencode
from bs4 import BeautifulSoup as BS

locale.setlocale(locale.LC_ALL, '')

MAX_INDEED_PAGE_RESULTS = 50

class IndeedScraper:
    """Indeed WebScraper"""

    def __init__(self, driver, db_obj=None):
        """Initialize the client with an API key."""
        self.driver = driver
        self.db_obj = db_obj
        self.base_url = "https://www.indeed.com/jobs"
        self._index_start = -1

    def find_jobs(self, job_filter):
        """Search for jobs on Indeed."""
        new_jobs = []
        search_params = self._get_search_params(job_filter)        
        new_page = self._get_new_page(search_params)
        while not IndeedScraper.is_last_page(new_page):
            page_jobs_dict = IndeedScraper.get_jobs_on_page(new_page)
            new_jobs.append(page_jobs_dict)
            new_page = self._get_new_page(search_params)
        return new_jobs

    def _get_search_params(self, job_filter):
        params = {
            "q": job_filter["keywords"],
            "l": job_filter.get("location", ""),
            "limit": job_filter.get("limit", MAX_INDEED_PAGE_RESULTS),
            "fromage": job_filter.get("posted_by", 3),
        }

        if job_filter.get("radius"):
            params["radius"] = IndeedScraper.nearest_radius(job_filter["radius"])
        if job_filter.get("remote"): 
            params["sc"] = "0kf:attr(DSQF7);"
        if job_filter.get("salary"):
            params["q"] +=  " " + locale.currency(
                job_filter["salary"], grouping=True)
        return params
        
    def _get_new_page(self, params):
        if self._index_start == -1:    
            self._index_start = 0
        else:
            self._index_start += MAX_INDEED_PAGE_RESULTS
        params["start"] = self._index_start
        search_url = self.base_url + "?" + urlencode(params)
        self.driver.get(search_url)
        soup = BS(self.driver.page_source, 'html.parser')
        return soup

    @staticmethod
    def is_last_page(page):
        return not bool(page.find(attrs={'data-testid':'pagination-page-next'}))
    
    @staticmethod
    def get_jobs_on_page(page):
        jobs_dict = {}
        jobs = page.select(".jobsearch-ResultsList .cardOutline")
        for job in jobs:
            job_data = IndeedScraper.get_job_data(job)
            jobs_dict[job_data['id']] = job_data
        return jobs_dict

    @staticmethod
    def get_job_data(job_element):
        class_data = [
            ('jobTitle', 'title'), ('companyName','company'), 
            ('companyLocation', 'location'), ('job-snippet','job_snippet'),
            ('metadata', 'metadata'), ('indeedApply','easy_apply')
        ]
        data = { new_name: 
            getattr(job_element.find(class_=class_name), "text", '')
            for class_name, new_name in class_data }
        
        data.update({
            'site':'indeed', 
            'id': IndeedScraper.get_job_id(job_element),
            })
        return data

    @staticmethod
    def get_job_id(job_element):
        for class_name in job_element.attrs['class']:
            if 'job_' in class_name:
                return class_name.replace("job",'indeed') 
        return

if __name__ == '__main__':
    from selenium import webdriver
    
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36")
    options.add_argument("--headless")
    config = {
        'driver': webdriver.Chrome(options=options),
        'job_filter': {
            "keywords": "devops",
            "posted_by": 3,
            "limit": 10,
            "remote": True
        }}
    
    scraper = IndeedScraper(config['driver'])
    page_jobs = scraper.find_jobs(config['job_filter'])
    for i,jobs in enumerate(page_jobs):
        print("Page:", i)
        for j, (job_id, job_data) in enumerate(jobs.items()):
            print(f"{j}. Job ID {job_id}")
            print(job_data)
    config['driver'].close() 