import sqlite3

def temperature_count():
	
	conn = sqlite3.connect('db.sqlite3')

	c = conn.cursor()

	#截至当日总计
	cursor = c.execute("SELECT views_count,id from doll_sites_photo")
	cursor = list(cursor)
	print(cursor)
	now_view = []
	for row in cursor:
		now_view.append((row))
	print(now_view)
	print("===> 截至当日总计\n")

	#截至昨日总计
	cursor = c.execute("SELECT history_views_count,id from doll_sites_photo")
	cursor = list(cursor)
	print(cursor)
	history_view = []
	for row in cursor:
		history_view.append(row)
	print(history_view)
	print("===> 截至昨日总计\n")

	#今日统计
	today_counts = []
	today_pk = []
	n = 0
	for view in now_view:
		today_pk.append(view[1])
		view = view[0] - history_view[n][0]
		today_counts.append(view)
		n += 1
	print(today_counts)
	print(today_pk)
	print("===> 今日统计\n")

	#当前热度
	cursor = c.execute("SELECT temperature,id from doll_sites_photo")
	cursor = list(cursor)
	print(cursor)
	temperature = []
	for row in cursor:
		temperature.append(row)
	print(temperature)
	print("===> 当前热度\n")

	n = 0
	for temper in temperature:
		pk = temper[1]
		temper = temper[0]*0.5632 + today_counts[n]
		temper = round(temper,3)
		updatesql = "UPDATE doll_sites_photo set temperature = %f where ID = %i" % (temper,pk)
		cursor = c.execute(updatesql)
		conn.commit()
		n += 1

	#更新history_view
	for view in now_view:
		pk = view[1]
		view = view[0]
		updatesql = "UPDATE doll_sites_photo set history_views_count = %f where ID = %i" % (view,pk)
		cursor = c.execute(updatesql)
		conn.commit()

	conn.close()
