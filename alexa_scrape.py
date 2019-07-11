#!/usr/bin/python
__author__ = "Justin Stals"

from bs4 import BeautifulSoup
import requests
import traceback

def get_site(url):
		
    domain_query = f'https://www.alexa.com/siteinfo/{url}'

    try:
        response = requests.get(domain_query)
        soup = BeautifulSoup(response.text, 'html.parser')
    except AttributeError:
        print('URL not found.')
        return None
    except Exception:
        print(traceback.print_exc())
        return None

    site_info = {
        'top_keywords' : get_top_keywords(soup),
        'similar_sites' : get_similar_sites(soup),
        'geography' : get_geography(soup),
        'engagement' : get_engagement(soup),
        'linksin' : get_linksin(soup) 
    }
    return site_info

def get_top_keywords(soup):
	topkw_div = soup.find("div", { "class" : "topkw" })
	if not topkw_div: return None
	topkw_list = [kw.text for kw in topkw_div.find_all("span", { "class" : "truncation" })]
	chunks = [topkw_list[x:x+3] for x in range(0, len(topkw_list), 3)]
	
	topkw_dict = {}

	for i in range(1, len(chunks)+1):
		topkw_dict[i] = { 
			'keyword' : chunks[i-1][0],
			'search_traffic' : chunks[i-1][1],
			'share_of_voice' : chunks[i-1][2]
		}

	return topkw_dict

def get_similar_sites(soup):
	ss_div = soup.find("div", { "class" : "audience" })
	if not ss_div: return None
	sites_list = [site.text for site in ss_div.find_all("a", { "class" : "truncation" })]
	sites_overlap = [ overlap.text.replace(',', '') for overlap in ss_div.find_all("span", { "class" : "truncation" })]

	for site_overlap in sites_overlap:
		try:
			site_overlap = float(site_overlap)
		except ValueError:
			site_overlap = None

	ss_dict = {}
	
	for i in range(0, len(sites_list)):
		ss_dict[sites_list[i]] = {
			'overlap' : sites_overlap[i*2],
			'alexa_rank' : sites_overlap[i*2 + 1]
		}

	return ss_dict

def get_geography(soup):
	geo_div = soup.find("div", { "class" : "geography" })
	if not geo_div: return None
	country_list = geo_div.find_all("li")
	country_dict = {}

	for li in country_list:
		name = li.find("div", { "id" : "countryName" }).text
		percent = li.find("div", { "id" : "countryPercent" }).text
		country_dict[name] = percent
	
	return country_dict

def get_engagement(soup):

	engagement_div = soup.find("section", { "class" : "engagement" })
	if not engagement_div: return None
	engagement_metrics = engagement_div.find_all("p", { "class" : "data" })
	metrics_text = [metric.text for metric in engagement_metrics]
	
	pageviews = metrics_text[0].split(' ')
	time_on_site = metrics_text[1].split(' ')
	bounce_rate = metrics_text[2].split(' ')

	engagement_dict = { 
		'pageviews' : { 
			'value' : None,
			'delta' : None
		},
		'time_on_site' : { 
			'value' : None,
			'delta' : None
		},
		'bounce_rate' : { 
			'value' : None,
			'delta' : None
		}
	}

	for l in [pageviews, time_on_site, bounce_rate]:
		for i in l:
			if '.' in i:
				if l == pageviews:
					if engagement_dict['pageviews']['value']:
						engagement_dict['pageviews']['delta'] = i
					else:
						engagement_dict['pageviews']['value'] = i

				if l == time_on_site:
					if engagement_dict['time_on_site']['value']:
						engagement_dict['time_on_site']['delta'] = i
					else:
						engagement_dict['time_on_site']['value'] = i

				if l == bounce_rate:
					if engagement_dict['bounce_rate']['value']:
						engagement_dict['bounce_rate']['delta'] = i
					else:
						engagement_dict['bounce_rate']['value'] = i

	return engagement_dict

def get_linksin(soup):
	linksin_div = soup.find("section", { "class" : "linksin" })
	linksin = linksin_div.find("span", { "class" : "data" }).text.replace(',', '')
	return int(linksin)