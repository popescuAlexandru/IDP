from flask import Flask
from flask import request, jsonify, Response
import uuid
import mysql.connector
import threading
import datetime

app = Flask(__name__)


@app.route('/get_optimal_route', methods=['GET'])
def get_optimal_route():
	try:
		source = request.args.get('source')
		dest = request.args.get('dest')
		departure_day = int(request.args.get('departure_day'))
		max_rides = int(request.args.get('max_rides'))
		if source is None or dest is None or departure_day is None or max_rides is None:
			return jsonify({'status': 'bad request'}), 200
		open = []
		mini = [(1 << 30), []]
		mydb.cmd_reset_connection()
		mycursor = mydb.cursor(buffered=True, dictionary=True)
		command = "select * from rides where departure_day={} and src='{}' and booked_tickets<available_seats*1.5;".format(departure_day, source)
		print(command)
		mycursor.reset()
		mycursor.execute(command)
		results = mycursor.fetchall()
		for result in results:
			# un nod este alcatuit din nr de curse, numarul de ore si lista de curse
			node = (1, [(result['departure_day'], result['departure_hour'], result['ride_id'], result['src'],
											result['dst'], result['duration'])])
			open.append(node)
		while len(open) > 0:
			# extragem prima stare din lista
			(current_depth, path) = open.pop(0)
			print(path)
			# daca am depasit adancimea salvam minimul si continuam
			if current_depth > max_rides:
				continue
			last_ride = path[-1]
			first_ride = path[0]
			if last_ride[4] == dest:
				time = (last_ride[0] - first_ride[0]) * 24 - first_ride[1] + last_ride[1] + last_ride[5]
				if time < mini[0]:
					mini[0] = time
					mini[1] = path
					continue
			day, hour, duration = last_ride[0], last_ride[1], last_ride[5]
			# generam ziua minima si ora minima de plecare pentru urmatorea cursa
			new_day, new_hour = day, hour + duration
			if new_hour >= 24:
				new_day += 1
				new_hour -= 24
			# daca am depasit anul curent
			if new_day > 365:
				continue
			# extragem vecinii
			command = "select * from rides where (departure_day>{} or (departure_day={} and departure_hour>={})) and src='{}'" \
					  "and booked_tickets<available_seats*1.5;".format(new_day, new_day, new_hour, last_ride[4])
			print(command)
			mycursor.reset()
			mycursor.execute(command)
			results = mycursor.fetchall()
			for result in results:
				# generam noul nod
				ride = (result['departure_day'], result['departure_hour'], result['ride_id'], result['src'], result['dst'], result['duration'])
				# daca nu am mai vizitat starea curente
				if result['dst'] not in [ride[3] for ride in path]:
					node = (current_depth + 1,
							path + [ride])
					# adaugam starea la stiva de noduri de explorat
					open = [node] + open
		mycursor.close()
		if mini[0] == (1<<30):
			return jsonify({'status': 'Unable to find optimal route', 'route': mini}), 200
		return jsonify({'status': 'OK', 'route': mini}), 200
	except Exception as err:
		return jsonify({'status': str(err), 'route': []}), 200


@app.route('/book_ticket', methods=['GET'])
def book_ticket():
	try:
		ride_ids = request.args.getlist('ride_ids[]')
		if ride_ids is None or len(ride_ids) == 0:
			return jsonify({'status': 'bad request', 'booking_id': ''}), 200
		booking_id = uuid.uuid4().hex
		print(booking_id)
		# Verifica pentru fiecare cursa daca exista si daca mai sunt bilete rezervate disponibile
		mydb.cmd_reset_connection()
		mycursor = mydb.cursor(buffered=True, dictionary=True)
		# Folosim un lock pentru a face verificarea daca cursele sunt valide cat si updatarea tabelelor
		with book_lock:
			for ride_id in ride_ids:
				command = "select booked_tickets, available_seats from rides where ride_id = '{}';".format(
					ride_id)
				mycursor.reset()
				mycursor.execute(command)
				print(ride_id, mycursor.rowcount)
				if mycursor.rowcount <= 0:
					mycursor.close()
					return jsonify({'status': 'Ride {} does not exist'.format(ride_id), 'booking_id': ''}), 200
				results = mycursor.fetchall()
				for result in results:
					if result['booked_tickets'] >= result['available_seats'] * 1.1:
						mycursor.close()
						return jsonify({'status': 'There are no more seats left for ride {}'.format(ride_id), 'booking_id': ''}), 200
			# Introduce in tabela bookings noua rezervare
			utc_datetime = datetime.datetime.utcnow()
			current_time = utc_datetime.strftime("%Y-%m-%d %H:%M:%S")
			command = "insert into bookings values('{}', false, '{}');".format(booking_id, current_time)
			mycursor.reset()
			mycursor.execute(command)
			# Updateaza numarul de bilete rezervate si introdu in tabela rides_booking asociearea dintre booking id si ride id
			for ride_id in ride_ids:
				command = "insert into rides_bookings values('{}', '{}');" \
						  "update rides set booked_tickets=booked_tickets+1 where ride_id='{}';".format(ride_id,
																											booking_id,
																											ride_id)
				mycursor.reset()
				for _ in mycursor.execute(command, multi=True):
					pass
			mycursor.close()
			mydb.commit()
			return jsonify({'status': 'OK', 'booking_id': booking_id}), 200
	except Exception as err:
		return jsonify({'status': str(err), 'booking_id': ''}), 200


@app.route('/buy_ticket', methods=['GET'])
def buy_ticket():
	try:
		reservation_id = request.args.get('reservation_id')
		credit_card = request.args.get('credit_card')
		if reservation_id is None or credit_card is None:
			return jsonify({'status': 'bad request', 'boarding_pass': ''}), 200
		# Extragem cursele cuprinse de rezervare
		ride_ids = []
		boardingPass = ''
		mydb.cmd_reset_connection()
		mycursor = mydb.cursor(buffered=True, dictionary=True)
		command = "select ride_id from rides_bookings where booking_id = '{}';".format(reservation_id)
		mycursor.execute(command)
		if mycursor.rowcount <= 0:
			mycursor.close()
			return jsonify({'status': 'Wrong booking id', 'boarding_pass': ''}), 200
		results = mycursor.fetchall()
		for result in results:
			ride_ids.append(result['ride_id'])
		# Verificam daca pentru toate cursele putem cumpara bilete
		with buy_lock:
			details = []
			for ride_id in ride_ids:
				command = "select * from rides where ride_id = '{}';".format(ride_id)
				print(command)
				mycursor.reset()
				mycursor.execute(command)
				print(ride_id, mycursor.rowcount)
				if mycursor.rowcount <= 0:
					mycursor.close()
					return jsonify({'status': 'Ride {} was canceled'.format(ride_id), 'boarding_pass': ''}), 200
				results = mycursor.fetchall()
				for result in results:
					if result['bought_tickets'] >= result['available_seats']:
						mycursor.close()
						return jsonify({'status': 'There are no more seats left for ride {}'.format(ride_id), 'boarding_pass': ''}), 200
					else:
						details.append((result['departure_day'], result['departure_hour'], result['ride_id'], result['src'],
										result['dst'], result['duration']))
			# Updatam numarul de bilete cumparate pentru fiecare cursa
			for ride_id in ride_ids:
				command = "update rides set bought_tickets=bought_tickets+1 where ride_id='{}'".format(ride_id)
				mycursor.reset()
				mycursor.execute(command)
			# Stergem din tabela booking_id rezervarea
			utc_datetime = datetime.datetime.utcnow()
			current_time = utc_datetime.strftime("%Y-%m-%d %H:%M:%S")
			command = "update bookings set bought=true and time='{}' where booking_id='{}'".format(current_time, reservation_id)
			mycursor.reset()
			mycursor.execute(command)
			# Salvam modificarile in baza de date
			mycursor.close()
			mydb.commit()
		# Sortam cursele dupa ziua si ora de plecare si construim informatia din boarding pass
		sorted(details, key=lambda x: (x[0], x[1]))
		boardingPass += '==========================================\n'\
						'==========================================\n'\
						'===============Boarding Pass==============\n'\
						'==========================================\n'\
						'==========================================\n'
		boardingPass += "Boarding Pass for booking {}:\n".format(reservation_id)
		for detail in details:
			boardingPass += 'DAY ' + str(detail[0]) + ', HOUR ' + str(detail[1]) + ': ' + 'ride ' \
							+ detail[2] + ' FROM ' + detail[3] + ' TO ' + detail[4] + ' duration ' + str(
				detail[5]) + ' hours\n'
		boardingPass += "Enjoy the ride!\n"
		return jsonify({'status': 'OK', 'boarding_pass': boardingPass}), 200
	except Exception as err:
		return jsonify({'status': str(err), 'boarding_pass': ''}), 200


def init_db():
	# Se creeaza tabelele in caz ca acestea nu exista
	try:
		mycursor = mydb.cursor()
		for _ in mycursor.execute(
				"""
					create table if not exists rides(
						ride_id varchar(50) primary key,
						src varchar(50) not null,
						dst varchar(50) not null,
						departure_hour integer not null check(departure_hour >= 0 and departure_hour <= 23),
						departure_day integer not null check (departure_day >= 1 and departure_day <= 365),
						duration integer not null check (duration > 0),
						price integer not null check (price > 0),
						available_seats integer not null check (available_seats > 0),
						booked_tickets integer default 0,
						bought_tickets integer default 0
					);
					
					create table if not exists bookings(
						booking_id varchar(50) primary key
						bought BOOLEAN,
						time varchar(255)
					);
					
					create table if not exists rides_bookings(
						ride_id varchar(50),
						booking_id varchar(50),
						FOREIGN KEY (ride_id) REFERENCES rides (ride_id) ON DELETE CASCADE,
						FOREIGN KEY (booking_id) REFERENCES bookings (booking_id) ON DELETE CASCADE
					);
				""",
				multi=True
		):
			pass
		mycursor.close()
		mydb.commit()
	except Exception as err:
		print(err)


if __name__ == '__main__':
	mydb = None
	book_lock = threading.Lock()
	buy_lock = threading.Lock()
	try:
		mydb = mysql.connector.connect(
			host="mysql",
			user="root",
			passwd="iamroot",
			database="rides"
		)
	except Exception as err:
		print('Cannot connect to database: ', err, '\n')
		exit(-1)

	if mydb.is_connected():
		print('connection established.')
		init_db()
	else:
		print('connection failed.')
		exit(-1)

	app.run('0.0.0.0', debug=True, port=16000)
