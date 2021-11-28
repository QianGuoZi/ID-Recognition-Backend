from flask import Flask, make_response, jsonify, request
import cv2
import pytesseract
import os
from PIL import Image
import numpy as np
import uuid

app = Flask(__name__)


@app.route('/',methods = ['GET', 'POST'])
def hello_world():
	bitmap = request.values.get('bitmap')
	# lastname = request.values.get('lastname')

	result = {
		'bitmap': bitmap,
		# 'lastname': lastname,
	}

	print(result)
	response = make_response(jsonify(result))
	response.headers['Access-Control-Allow-Origin'] = '*'
	response.headers['Access-Control-Allow-Methods'] = '*'
	response.headers['Access-Control-Allow-Headers'] = '*'
	return response


@app.route('/rt0',methods = ['GET', 'POST'])
def rt0():
	img = request.files.get('image')
	# print(type(img))

	if img:
		f = open ('./bitmap.jpeg','wb')
		data = img.read()
		f.write(data)
		f.close()

		img = cv2.imread('./bitmap.jpeg')
		# print(img.shape)

		_, w, _ = img.shape
		if w > 800:
			print('The picture is too large, you had better to find another one!')
			img = cv2.resize(img, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_AREA)
			print(img.shape)

		# 形态学 kernel
		kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

		# 失败 速度太慢
		# mean_img = cv2.pyrMeanShiftFiltering(img, sp=20, sr=30)
		# img_canny = cv2.Canny(mean_img, 150, 300)

		# 灰度化
		gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

		# 二值化
		_, binary_img = cv2.threshold(gray_img, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
		# binary_img = cv2.adaptiveThreshold(gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 155, 1)

		# 腐蚀 待调参
		erode_img = cv2.erode(binary_img, kernel, iterations=8)

		# 闭操作 待调参
		# close_img = cv2.morphologyEx(erode_img, cv2.MORPH_CLOSE, kernel, iterations=8)

		# 轮廓查找
		# contours, _ = cv2.findContours(close_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		contours, _ = cv2.findContours(erode_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		
		# 记录所有符合条件的矩形
		rects = []

		# 遍历轮廓
		for (_, contour) in enumerate(contours):
			# 求出宽高
			x, y, w, h = cv2.boundingRect(contour)
			# 在符合条件的基础上 进行矩形框绘制
			if (w > h * 6) and (w < h * 18) and (w * h >= 3000):
				# 绘制红框
				rect = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
				# 把矩形添加到数组中
				rects.append({'x': x, 'y': y, 'w': w, 'h': h})

		if rects.__len__() < 1:
			print('You input is not standard')
			exit()

		# 继续查找坐标最低的矩形区域
		final_rect = rects[0]
		for (_, rect) in enumerate(rects):
			if rect['y'] + rect['h'] > final_rect['y'] + final_rect['h']:
				final_rect = rect.copy()

		# 膨胀
		# dilate_img = cv2.dilate(binary_img, kernel, iterations=1)

		# 截取区域
		dst = img[final_rect['y']:(final_rect['y'] + final_rect['h']),
			  final_rect['x']:(final_rect['x'] + final_rect['w'])]

		# 获取文本
		# 待调参
		# text = pytesseract.image_to_string(dst, lang="chi_sim+eng", config='--psm 7 --oem 3')
		# text = pytesseract.image_to_string(dst, lang="eng", config='--psm 8')
		text = pytesseract.image_to_string(dst, lang="eng", config='--psm 7 --oem 3')
		text1 = text.replace(' ','')
		text2 = text1.replace('\n', '')
		text3 = text2.replace('\f', '')

		result = {
			'text' : text3.replace(' ', ''),
		}
		response = make_response(jsonify(result))
		response.headers['Access-Control-Allow-Origin'] = '*'
		response.headers['Access-Control-Allow-Methods'] = '*'
		response.headers['Access-Control-Allow-Headers'] = '*'
		return response


@app.route('/rt2', methods=['GET', 'POST'])
def rt2():
	img = request.files.get('image')
	# print(type(img))

	if img:
		f = open('./bitmap.jpeg', 'wb')
		data = img.read()
		f.write(data)
		f.close()

		img = cv2.imread('./bitmap.jpeg')
		# print(img.shape)

		_, w, _ = img.shape
		if w > 800:
			print('The picture is too large, you had better to find another one!')
			img = cv2.resize(img, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_AREA)
			print(img.shape)

		# 形态学 kernel
		kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

		# 失败 速度太慢
		# mean_img = cv2.pyrMeanShiftFiltering(img, sp=20, sr=30)
		# img_canny = cv2.Canny(mean_img, 150, 300)

		# 灰度化
		gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		# print('gray')
		# print(gray_img.shape)

		# 二值化
		_, binary_img = cv2.threshold(gray_img, 150, 255, cv2.THRESH_BINARY)
		# binary_img = cv2.adaptiveThreshold(gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 155, 1)

		# 腐蚀 待调参
		erode_img = cv2.erode(binary_img, kernel, iterations=8)

		# 生成随机hash
		uuid_value = uuid.uuid1()
		uuid_int = uuid_value.int
		print("uuid_int: ", uuid_int)

		file_name = str(uuid_int) + 'result.jpeg'

		cv2.imwrite('static\\' + file_name, erode_img)

		result = {
			# 'url': r"D:\Python\try\static\result.jpeg",
			'url' : "http:\\127.0.0.1:5000\\static\\" + file_name
		}



		response = make_response(jsonify(result))
		response.headers['Access-Control-Allow-Origin'] = '*'
		response.headers['Access-Control-Allow-Methods'] = '*'
		response.headers['Access-Control-Allow-Headers'] = '*'
		return response


@app.route('/rt3', methods=['GET', 'POST'])
def rt3():
	img = request.files.get('image')
	# print(type(img))

	if img:
		f = open('./bitmap.jpeg', 'wb')
		data = img.read()
		f.write(data)
		f.close()

		img = cv2.imread('./bitmap.jpeg')
		# print(img.shape)

		_, w, _ = img.shape
		if w > 800:
			print('The picture is too large, you had better to find another one!')
			img = cv2.resize(img, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_AREA)
			print(img.shape)

		# 形态学 kernel
		kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

		# 失败 速度太慢
		# mean_img = cv2.pyrMeanShiftFiltering(img, sp=20, sr=30)
		# img_canny = cv2.Canny(mean_img, 150, 300)

		# 灰度化
		gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

		# 二值化
		_, binary_img = cv2.threshold(gray_img, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
		# binary_img = cv2.adaptiveThreshold(gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 155, 1)

		# 腐蚀 待调参
		erode_img = cv2.erode(binary_img, kernel, iterations=8)

		# 闭操作 待调参
		# close_img = cv2.morphologyEx(erode_img, cv2.MORPH_CLOSE, kernel, iterations=8)

		# 轮廓查找
		# contours, _ = cv2.findContours(close_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		contours, _ = cv2.findContours(erode_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		# 记录所有符合条件的矩形
		rects = []

		# 遍历轮廓
		for (_, contour) in enumerate(contours):
			# 求出宽高
			x, y, w, h = cv2.boundingRect(contour)
			# 在符合条件的基础上 进行矩形框绘制
			if (w > h * 6) and (w < h * 18) and (w * h >= 3000):
				# 绘制红框
				rect = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
				# 把矩形添加到数组中
				rects.append({'x': x, 'y': y, 'w': w, 'h': h})

		if rects.__len__() < 1:
			print('You input is not standard')
			exit()

		# 继续查找坐标最低的矩形区域
		final_rect = rects[0]
		for (_, rect) in enumerate(rects):
			if rect['y'] + rect['h'] > final_rect['y'] + final_rect['h']:
				final_rect = rect.copy()

		# 膨胀
		# dilate_img = cv2.dilate(binary_img, kernel, iterations=1)

		# 截取区域
		dst = img[final_rect['y']:(final_rect['y'] + final_rect['h']),
			  final_rect['x']:(final_rect['x'] + final_rect['w'])]

		# 获取文本
		# 待调参
		# text = pytesseract.image_to_string(dst, lang="chi_sim+eng", config='--psm 7 --oem 3')
		# text = pytesseract.image_to_string(dst, lang="eng", config='--psm 8')
		# text = pytesseract.image_to_string(dst, lang="eng", config='--psm 7 --oem 3')
		# text1 = text.replace(' ', '')
		# text2 = text1.replace('\n', '')
		# text3 = text2.replace('\f', '')


		uuid_value = uuid.uuid1()
		uuid_int = uuid_value.int
		print("uuid_int: ", uuid_int)

		file_name = str(uuid_int) + 'result.jpeg'

		cv2.imwrite('static\\' + file_name, dst)

		result = {
			# 'url': r"D:\Python\try\static\result.jpeg",
			'url' : "http:\\127.0.0.1:5000\\static\\" + file_name
		}
		response = make_response(jsonify(result))
		response.headers['Access-Control-Allow-Origin'] = '*'
		response.headers['Access-Control-Allow-Methods'] = '*'
		response.headers['Access-Control-Allow-Headers'] = '*'
		return response


@app.route('/rt4', methods=['GET', 'POST'])
def rt4():
	img = request.files.get('image')

	if img:
		f = open('./bitmap.jpeg', 'wb')
		data = img.read()
		f.write(data)
		f.close()

		img = cv2.imread('./bitmap.jpeg')

		# cv2.imshow('img', img)
		# cv2.waitKey(0)

		_, w, _ = img.shape
		if w > 800:
			print('The picture is too large, you had better to find another one!')
			img = cv2.resize(img, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_AREA)
			print(img.shape)

		text = pytesseract.image_to_string(img, lang="eng", config='--psm 7 --oem 3')
		text1 = text.replace(' ', '')
		text2 = text1.replace('\n', '')
		text3 = text2.replace('\f', '')

		result = {
			'text': text3.replace(' ', ''),
		}
		response = make_response(jsonify(result))
		response.headers['Access-Control-Allow-Origin'] = '*'
		response.headers['Access-Control-Allow-Methods'] = '*'
		response.headers['Access-Control-Allow-Headers'] = '*'
		return response



# 不符合架构需求
# @app.route('/rt4', methods=['GET', 'POST'])
# def rt4():
# 	img = request.files.get('image')
# 	# print(type(img))
#
# 	if img:
# 		f = open('./bitmap.jpeg', 'wb')
# 		data = img.read()
# 		f.write(data)
# 		f.close()
#
# 		img = cv2.imread('./bitmap.jpeg')
# 		# print(img.shape)
#
# 		_, w, _ = img.shape
# 		if w > 800:
# 			print('The picture is too large, you had better to find another one!')
# 			img = cv2.resize(img, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_AREA)
# 			print(img.shape)
#
# 		# 形态学 kernel
# 		kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
#
# 		# 失败 速度太慢
# 		# mean_img = cv2.pyrMeanShiftFiltering(img, sp=20, sr=30)
# 		# img_canny = cv2.Canny(mean_img, 150, 300)
#
# 		# 灰度化
# 		gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#
# 		contours, _ = cv2.findContours(gray_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#
# 		# 记录所有符合条件的矩形
# 		rects = []
#
# 		# 遍历轮廓
# 		for (_, contour) in enumerate(contours):
# 			# 求出宽高
# 			x, y, w, h = cv2.boundingRect(contour)
# 			# 在符合条件的基础上 进行矩形框绘制
# 			if (w > h * 6) and (w < h * 18) and (w * h >= 3000):
# 				# 绘制红框
# 				rect = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
# 				# 把矩形添加到数组中
# 				rects.append({'x': x, 'y': y, 'w': w, 'h': h})
#
# 		if rects.__len__() < 1:
# 			print('You input is not standard')
# 			exit()
#
# 		# 继续查找坐标最低的矩形区域
# 		final_rect = rects[0]
# 		for (_, rect) in enumerate(rects):
# 			if rect['y'] + rect['h'] > final_rect['y'] + final_rect['h']:
# 				final_rect = rect.copy()
#
# 		# 膨胀
# 		# dilate_img = cv2.dilate(binary_img, kernel, iterations=1)
#
# 		# 截取区域
# 		dst = img[final_rect['y']:(final_rect['y'] + final_rect['h']),
# 			  final_rect['x']:(final_rect['x'] + final_rect['w'])]
#
# 		text = pytesseract.image_to_string(dst, lang="eng", config='--psm 7 --oem 3')
# 		text1 = text.replace(' ', '')
# 		text2 = text1.replace('\n', '')
# 		text3 = text2.replace('\f', '')
#
# 		print(text.replace(' ', ''))
# 		cv2.imshow('gray_img', gray_img)
# 		cv2.imshow('img', img)
# 		cv2.imshow('dst', dst)
# 		cv2.waitKey(0)
# 		cv2.destroyAllWindows()
#
# 		result = {
# 			'text': text3.replace(' ', ''),
# 		}
# 		response = make_response(jsonify(result))
# 		response.headers['Access-Control-Allow-Origin'] = '*'
# 		response.headers['Access-Control-Allow-Methods'] = '*'
# 		response.headers['Access-Control-Allow-Headers'] = '*'
# 		return response








if __name__ == '__main__':
	app.run()


