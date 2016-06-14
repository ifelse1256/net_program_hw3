import argparse, requests
from urllib.parse import urljoin,urlsplit
from lxml import etree
import re

email_list = []

def in_list(email_iter):
	global email_list
	for each_mail in email_list:
		if each_mail == email_iter:
			return True
	return False

def GET(url):
	global email_list
	response = requests.get(url)
	if response.headers.get('Content-Type','').split(';')[0] != 'text/html':
		return
	text = response.text
	#print('text:'+text)

	email = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",text)

	for email_iter in email:
		email_iter = str(email_iter)
		if len(email_list)==0:
			email_list.append(email_iter)
		else:
			judge = in_list(email_iter)
			if judge == False:
				email_list.append(email_iter)
				print('email:{0}'.format(email_iter))
				print('number:{0}'.format(len(email_list)))

	'''for email_iter in email:
		if email_iter not in email_list:
			print('email:'+email_iter)
			email_list.update(email_iter)'''

	try:
		html = etree.HTML(text)  # parse html content
	except Exception as e:
		print('catch html is failure')
		return
	links = html.findall('.//a[@href]')#links function address
	
	for link in links: 
		yield GET,urljoin(url, link.attrib['href'])


def main(GET):
	parser = argparse.ArgumentParser(description='scrape a CSIE')
	parser.add_argument('url',help='the URL at which begin')
	start_url = parser.parse_args().url
	starting_netloc = urlsplit(start_url).netloc
	url_filter = (lambda url: urlsplit(url).netloc == starting_netloc)
	print('url_filter:'+str(type(url_filter)))
	scrape((GET,start_url), url_filter)

def scrape(start, url_filter):
	futher_work  = {start}
	already_seen = {start}
	while futher_work:
		call_tuple = futher_work.pop()
		function, url, *etc = call_tuple
		print(function.__name__,url,*etc)
		for call_tuple in function(url,*etc):
			if call_tuple in already_seen:
				continue
			already_seen.add(call_tuple)
			function, url, *etc = call_tuple
			if not url_filter(url):
				continue
			futher_work.add(call_tuple)

if __name__=='__main__':
	main(GET)


