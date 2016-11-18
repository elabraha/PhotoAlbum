'''
Tests API routes for part 2a and 2b of EECS 485 Project 3
Requires "requests" library installed (pip install requests)
Expects database to be in default state (drop tables, then run tbl_create.sql, load_data.sql and pa3_sql.sql)
Example usage:
python test_pic_api.py hostname:port 
python test_pic_api.py http://eecs485-03.eecs.umich.edu:5930/secretkey/pa3
OR
python test_pic_api.py http://localhost:5930/secretkey/pa3
'''
import sys
import unittest

import requests

class TestPicCaptionAPI(unittest.TestCase):

	def __init__(self, testName='runTest', hostname=None):
		super(TestPicCaptionAPI, self).__init__(testName)
		if hostname is None:
			raise ValueError('You must pass in a hostname.')
		self.base_caption_url = '{0}/pic/caption'.format(hostname)

	def test_caption_get_basic(self):
		r = requests.get(self.base_caption_url, params={'id': 'football_s3'})
		corr_resp = {
			'caption': 'What do you want me to do?'
		}
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 200)

	def test_caption_get_blank_caption(self):
		r = requests.get(self.base_caption_url, params={'id': 'football_s2'})
		corr_resp = {
			'caption': ''
		}
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 200)

	def test_caption_get_no_id(self):
		r = requests.get(self.base_caption_url)
		corr_resp = {
			'error': 'You did not provide an id parameter.',
			'status': 404
		}
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 404)

	def test_caption_get_invalid_id(self):
		r = requests.get(self.base_caption_url, params={'id': 'football_s5'})
		corr_resp = {
			'error': 'Invalid id parameter. The picid does not exist.',
			'status': 422
		}
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 422)

	def test_caption_post_basic(self):
		payload = {
			'id': 'football_s2',
			'caption': 'This is an updated caption!'
		}
		corr_resp = {
			'caption': 'This is an updated caption!',
			'status': 201
		}
		r = requests.post(self.base_caption_url, json=payload)
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 201)

	def test_caption_post_update(self):
		payload = {
			'id': 'football_s3',
			'caption': 'Changing the caption!'
		}
		corr_resp = {
			'caption': 'Changing the caption!',
			'status': 201
		}
		r = requests.post(self.base_caption_url, json=payload)
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 201)

	def test_caption_post_no_caption_id(self):
		payload = {
			'fakekey': 'fakevalue'
		}
		corr_resp = {
			'error': 'You did not provide an id and caption parameter.',
			'status': 404
		}
		r = requests.post(self.base_caption_url, json=payload)
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 404)

	def test_caption_post_no_id(self):
		payload = {
			'caption': 'Caption that shouldn\'t update.'
		}
		corr_resp = {
			'error': 'You did not provide an id parameter.',
			'status': 404
		}
		r = requests.post(self.base_caption_url, json=payload)
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 404)

	def test_caption_post_no_caption(self):
		payload = {
			'id': 'football_s3'
		}
		corr_resp = {
			'error': 'You did not provide a caption parameter.',
			'status': 404
		}
		r = requests.post(self.base_caption_url, json=payload)
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 404)

	def test_caption_post_invalid_picid(self):
		payload = {
			'id': 'football_s5',
			'caption': 'This is a caption that will never exist.'
		}
		corr_resp = {
			'error': 'Invalid id. The picid does not exist.',
			'status': 422
		}
		r = requests.post(self.base_caption_url, json=payload)
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 422)

class TestPicFavoriteAPI(unittest.TestCase):

	def __init__(self, testName='runTest', hostname=None):
		super(TestPicFavoriteAPI, self).__init__(testName)
		if hostname is None:
			raise ValueError('You must pass in a hostname.')
		self.base_favorite_url = '{0}/pic/favorites'.format(hostname)

	def test_favorite_get_basic1(self):
		corr_resp = {
			'id': 'football_s2',
			'num_favorites': 3,
			'latest_favorite': 'sportslover'
		}
		r = requests.get(self.base_favorite_url, params={'id': 'football_s2'})
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 200)

	def test_favorite_get_basic2(self):
		corr_resp = {
			'id': 'football_s3',
			'num_favorites': 2,
			'latest_favorite': 'spacejunkie'
		}
		r = requests.get(self.base_favorite_url, params={'id': 'football_s3'})
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 200)

	def test_favorite_get_basic3(self):
		corr_resp = {
			'id': 'football_s4',
			'num_favorites': 0,
			'latest_favorite': ''
		}
		r = requests.get(self.base_favorite_url, params={'id': 'football_s4'})
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 200)

	def test_favorite_get_no_id(self):
		corr_resp = {
			'error': 'You did not provide an id parameter.',
			'status': 404
		}
		r = requests.get(self.base_favorite_url)
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 404)

	def test_favorite_get_invalid_id(self):
		corr_resp = {
			'error': 'Invalid id parameter. The picid does not exist.',
			'status': 422
		}
		r = requests.get(self.base_favorite_url, params={'id': 'football_s5'})
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 422)

	def test_favorite_post_basic1(self):
		payload = {
			'id': 'football_s3',
			'username': 'traveler'
		}
		corr_resp = {
			'id': 'football_s3',
			'status': 201
		}
		r = requests.post(self.base_favorite_url, json=payload)
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 201)

	def test_favorite_post_no_id_username(self):
		payload = {
			'fakekey': 'fakevalue'
		}
		# spec originally had this
		corr_resp1 = {
			'error': 'You did not provide an id and caption parameter.',
			'status': 404
		}
		# spec now has this
		corr_resp2 = {
			'error': 'You did not provide an id and username parameter.',
			'status': 404
		}
		r = requests.post(self.base_favorite_url, json=payload)
		assertions = []
		try:
			self.assertEqual(r.json(), corr_resp1)
		except AssertionError as e:
			assertions.append(e)
		try:
			self.assertEqual(r.json(), corr_resp2)
		except AssertionError as e:
			assertions.append(e)

		if len(assertions) == 2:
			raise AssertionError(assertions[0])

		self.assertEqual(r.status_code, 404)

	def test_favorite_post_no_id(self):
		payload = {
			'username': 'sportslover'
		}
		corr_resp = {
			'error': 'You did not provide an id parameter.',
			'status': 404
		}
		r = requests.post(self.base_favorite_url, json=payload)
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 404)

	def test_favorite_post_no_username(self):
		payload = {
			'id': 'football_s2'
		}
		corr_resp = {
			'error': 'You did not provide a username parameter.',
			'status': 404
		}
		r = requests.post(self.base_favorite_url, json=payload)
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 404)

	def test_favorite_post_invalid_picid(self):
		payload = {
			'id': 'football_s5',
			'username': 'spacejunkie'
		}
		corr_resp = {
			'error': 'Invalid id. The picid does not exist.',
			'status': 422
		}
		r = requests.post(self.base_favorite_url, json=payload)
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 422)

	def test_favorite_post_invalid_username(self):
		payload = {
			'id': 'football_s3',
			'username': 'invalidusername'
		}
		corr_resp = {
			'error': 'Invalid username. The username does not exist.',
			'status': 422
		}
		r = requests.post(self.base_favorite_url, json=payload)
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 422)

	def test_favorite_post_username_already_favorited(self):
		payload = {
			'id': 'football_s2',
			'username': 'sportslover'
		}
		corr_resp = {
			'error': 'The user has already favorited this photo.',
			'status': 403
		}
		r = requests.post(self.base_favorite_url, json=payload)
		self.assertEqual(r.json(), corr_resp)
		self.assertEqual(r.status_code, 403)




if __name__ == "__main__":
	if len(sys.argv) < 2:
		sys.exit('You must pass in the hostname:port/secretkey/pa3 as a command line argument. Example usage: python test_pic_api.py http://localhost:5930/secretkey/pa3')
	
	hostname = sys.argv[1]

	# Test Caption routes
	caption_tests = ['test_caption_get_basic', 'test_caption_get_blank_caption', 'test_caption_get_no_id', 'test_caption_get_invalid_id',
			 'test_caption_post_basic', 'test_caption_post_update', 'test_caption_post_no_caption_id', 'test_caption_post_no_id',
			 'test_caption_post_no_caption', 'test_caption_post_invalid_picid']
	suite = unittest.TestSuite([TestPicCaptionAPI(f, hostname) for f in caption_tests])
	unittest.TextTestRunner(verbosity=2).run(suite)

	# Test Favorite routes
	favorite_tests = ['test_favorite_get_basic1', 'test_favorite_get_basic2', 'test_favorite_get_basic3',
					  'test_favorite_get_no_id','test_favorite_get_invalid_id','test_favorite_post_basic1',
					  'test_favorite_post_no_id_username','test_favorite_post_no_id','test_favorite_post_no_username',
					  'test_favorite_post_invalid_picid','test_favorite_post_invalid_username',
					  'test_favorite_post_username_already_favorited']
	suite = unittest.TestSuite([TestPicFavoriteAPI(f, hostname) for f in favorite_tests])
	unittest.TextTestRunner(verbosity=2).run(suite)