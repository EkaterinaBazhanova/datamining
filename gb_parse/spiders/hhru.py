import scrapy
import requests

from gb_parse.loaders import HhruLoader

class HhruSpider(scrapy.Spider):
	name = 'hhru'
	allowed_domains = ['hh.ru']
	start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

	_xpath_selectors = {
		"pagination": "//div[@data-qa='pager-block']/a[@class='bloko-button']/@href",
		"vacancy": "//a[@data-qa='vacancy-serp__vacancy-title']/@href"
	}

	_xpath_data_vacancy = {
	"vacancy_title": "//h1[@class='bloko-header-1']/text()",
	"salary": "//p[contains(@class, 'vacancy-salary')]/span[contains(@class,'bloko-header-2')]/text()",
	"description": "//div[contains(@class,'vacancy-description')]//div[@class='g-user-content']//text() | //div[contains(@data-qa,'vacancy-description')]//text()",
	"skills": "//div[@class='bloko-tag-list']/div//text()",
	}

	_xpath_data_company = {
		"employer_name": "//div[contains(@class, 'employer-sidebar-header')]//div//h1[contains(@class, 'bloko-header-1')]//span[contains(@class, 'company-header-title-name')]/text()",
		"employer_url": "//div[contains(@class, 'employer-sidebar')]//div[contains(@class, 'employer-sidebar-content')]//a[contains(@class, 'g-user-content')]/@href",
		"employer_activity": "//div[contains(@class, 'employer-sidebar')]//div[contains(@class, 'employer-sidebar-content')]//p/text()",
		"employer_description": "//div[contains(@class, 'company-description')]//div[contains(@class, 'g-user-content')]//text()",
		"employer_vacancies": "//div[contains(@class, 'company-vacancies-group')]//span[contains(@class, 'bloko-link-switch')]/text()"
	}

	def _get_follow_xpath(self, response, selector, callback, **kwargs):
		for link in response.xpath(selector):
			yield response.follow(link, callback=callback, cb_kwargs=kwargs)

	def parse(self, response, *args, **kwargs):
		yield from self._get_follow_xpath(
			response, self._xpath_selectors["pagination"], self.parse
		)

		yield from self._get_follow_xpath(
			response, self._xpath_selectors["vacancy"], self.vacancy_parse
		)


	def vacancy_parse(self, response):
		loader = HhruLoader(response=response)
		for key, selector in self._xpath_data_vacancy.items():
			loader.add_xpath(key, selector)


		employer = response.xpath("//a[contains(@class, 'vacancy-company-name')]/@href").extract_first()
		employer_page = f"https://hh.ru{employer}"

		yield response.follow(employer_page, callback=self.employer_parse, cb_kwargs=loader.load_item())


	def employer_parse(self, response, **kwargs):
		loader = HhruLoader(response=response)
		for key, value in response.cb_kwargs.items():
			loader.add_value(key, value)
		loader.add_value("company_url", response.url)
		for key, selector in self._xpath_data_company.items():
			loader.add_xpath(key, selector)
		yield loader.load_item()
