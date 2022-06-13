from sre_constants import SUCCESS
from xml.sax.handler import property_interning_dict
from requests import api
from telegram import Telegram
import requests
from config import url_lists, authorization_header, platform, accepted_total_execution_time, x_device_id, X_Secret_Key
import time
from random import randint, shuffle
import asyncio
import aiohttp

async def async_hit(session, url):
	start_time = time.time()
	headers = {'Authorization': authorization_header, 'platform': platform, 'X-Device-Id': x_device_id, 'X-Secret-Key': X_Secret_Key}
	async with session.get(url, headers=headers) as resp:
		# print(url)
		# print(resp.status)
		# print(await resp.text())
		if resp.status == 200:
			body = await resp.text()
			if body.find('Token tidak valid') != -1:
				rnd_number = randint(100, 500)
				return [url, resp.status, 'INVALID_TOKEN', rnd_number]
			elif body.find('Missing parameter platform code') != -1:
				rnd_number = randint(501, 999)
				return [url, resp.status, 'MISSING_PLATFORM_CODE', rnd_number]
			
			end_time = time.time()
			total_time = end_time - start_time
			result_str = f'{url}.. {total_time:.2f} seconds'
			return [url, resp.status, 'OK', total_time]
		else:
			rnd_number = randint(1000, 9999)
			return [url, resp.status, 'ERROR', rnd_number]
			

async def async_main():
	t = Telegram()
	# t.deactivate()
	result_dict = {}
	total_execution_time = 0
	total_time = 0
	stats = {}
	stats['all_apis'] = len(url_lists)
	stats['apis_ok'] = 0
	stats['apis_invalid_token'] = 0
	stats['apis_error'] = 0
	stats['apis_missing_platform_code'] = 0
	urls_error = []
	urls_invalid_token = []
	urls_missing_platform_code = []
	t.sendSimpleMessage('///// API Monitor Request is running...')

	execution_start_time = time.time()
	async with aiohttp.ClientSession() as session:
		tasks = []
		shuffle(url_lists)
		for url in url_lists:
			tasks.append(asyncio.ensure_future(async_hit(session, url)))

		all_results = await asyncio.gather(*tasks)
		for result in all_results:
			result_dict[result[3]] = result[0]
			result.append(result_dict)
			if result[2] == 'OK':
				total_time = total_time + result[3]
				stats['apis_ok'] = stats['apis_ok'] + 1
			elif result[2] == 'ERROR':
				stats['apis_error'] = stats['apis_error'] + 1
				urls_error.append(f'{result[1]} - {result[0]}')
			elif result[2] == 'INVALID_TOKEN':
				stats['apis_invalid_token'] = stats['apis_invalid_token'] + 1
				urls_invalid_token.append(result[0])
			elif result[2] == 'MISSING_PLATFORM_CODE':
				stats['apis_missing_platform_code'] = stats['apis_missing_platform_code'] + 1
				urls_missing_platform_code.append(result[0])
	total_execution_time = time.time() - execution_start_time

	api_results = ''
	for i in sorted(result_dict.keys(), reverse=True):
		result = f'{i:.2f} : {result_dict[i]}'
		api_results = api_results + "\n" + result

	if (total_execution_time >= accepted_total_execution_time):
		t.tprint(api_results)
		t.sendMessage(api_results)
	
	t.sendSimpleMessage('Done.')

	if stats['apis_invalid_token'] > 0:
		summary_invalid_token = f'{stats["apis_invalid_token"]} invalid token(s):'
		for url in urls_invalid_token:
			summary_invalid_token = summary_invalid_token + "\n" + f'{url}'
		t.tprint(f'{summary_invalid_token}' + "\n")
		t.sendMessage(summary_invalid_token)

	if stats['apis_missing_platform_code'] > 0:
		summary_missing_platform_code = f'{stats["apis_missing_platform_code"]} missing platform code:'		
		for url in urls_missing_platform_code:
			summary_missing_platform_code = summary_missing_platform_code + "\n" + f'{url}'
		t.tprint(f'{summary_missing_platform_code}' + "\n")
		t.sendMessage(summary_missing_platform_code)
	
	if stats['apis_error'] > 0:
		summary_error = f'{stats["apis_error"]} error(s):'
		for url in urls_error:
			summary_error = summary_error + "\n" + f'{url}'
		t.tprint(f'{summary_error}' + "\n")
		t.sendMessage(summary_error)
		print(SUCCESS)
	summary = ''
	
	result_str = f'{total_time:.2f} seconds'
	summary = f'Total execution time: {total_execution_time:.2f} seconds'
	summary = summary + "\n" + f'Total API time: {result_str}'
	summary = summary + "\n" + f'Total APIs: {stats["all_apis"]}'
	summary = summary + "\n" + f'Total OK: {stats["apis_ok"]}'
	summary = summary + "\n" + f'Total Error: {stats["apis_error"]}'
	summary = summary + "\n" + f'Total Invalid Token: {stats["apis_invalid_token"]}'
	summary = summary + "\n" + f'Total Missing Platform Code: {stats["apis_missing_platform_code"]}'
	summary = summary + "\n" + 'See ya!' + "\n" + '/////'
	t.tprint(summary)
	t.tprint(urls_error)
	t.sendMessage(summary)
	print(SUCCESS)


asyncio.run(async_main())


# if __name__ == '__main__':
# 	main()
