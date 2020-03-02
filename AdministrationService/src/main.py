from flask import Flask
from flask import request, jsonify, Response
import mysql.connector

app = Flask(__name__)


@app.route('/add_ride', methods=['POST'])
def add_ride():
	payload = request.get_json(silent=True)
	if not payload:
		return jsonify({'status': 'bad request'}), 400
	else:
		try:
			# Inseram informatiile legate de zbor in tabela flights
			mydb.cmd_reset_connection()
			mycursor = mydb.cursor()
			command = "INSERT INTO rides(src, dst, departure_day, departure_hour, duration, available_seats, ride_id, price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
			values = (payload.get('source'), payload.get('dest'), int(payload.get('departure_day')),
					  int(payload.get('departure_hour')), int(payload.get('duration')),
					  int(payload.get('number_of_seats')), payload.get('flight_id')), int(payload.get('price')),
			mycursor.execute(command, values)
			mycursor.close()
			mydb.commit()
			return jsonify({'status': 'Ride added'}), 200
		except mysql.connector.IntegrityError as err:
			return jsonify({'status': "Integrity error: {}".format(err)}), 400
		except mysql.connector.DataError as err:
			return jsonify({'status': "Data error: {}".format(err)}), 400
		except Exception as err:
			return jsonify({'status': str(err)}), 400


@app.route('/cancel_ride', methods=['POST'])
def cancel_ride():
	payload = request.get_json(silent=True)
	if not payload:
		return jsonify({'status': 'bad request'}), 400
	else:
		try:
			# !!! Intai stergem din tabela bookings deoarece daca stergem din tabela rides (foreign key-ul fiind de
			# tipul on delete cascade) se vor sterge din tabela rides_bookings intrarile asociate zborului si nu vom
			# mai stii care booking-uri trebuiesc anulate

			# Stergem rezervarile facute pentru acest zbor din tabela bookings
			# Stergem informatiile legate de zbor din tabela flights
			mydb.cmd_reset_connection()
			mycursor = mydb.cursor()
			command = "delete from bookings where booking_id in (select distinct booking_id from rides_bookings where ride_id = '{}');"\
					  "delete from rides where ride_id = '{}';".format(payload.get('ride_id'), payload.get('ride_id'))
			found = False
			for rez in mycursor.execute(command, multi=True):
				if rez.rowcount != 0:
					found = True
			mycursor.close()
			mydb.commit()
			if found:
				return jsonify({'status': 'Flight deleted'}), 200
			return jsonify({'status': 'Ride does not exist'}), 400
		except mysql.connector.IntegrityError as err:
			return jsonify({'status': "Integrity error: {}".format(err)}), 400
		except mysql.connector.DataError as err:
			return jsonify({'status': "Data error: {}".format(err)}), 400
		except Exception as err:
			return jsonify({'status': str(err)}), 400


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
					);
					
					create table if not exists rides_bookings(
						ride_id varchar(50),
						booking_id varchar(50),
						FOREIGN KEY (ride_id) REFERENCES rides (ride_id),
						FOREIGN KEY (booking_id) REFERENCES bookings (booking_id)
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
	try:
		mydb = mysql.connector.connect(
			host="mysql",
			user="root",
			passwd="iamroot",
			database="rides"
		)
	except Exception as err:
		print("Cannot connect to database: ", err, '\n')
		exit(-1)

	if mydb.is_connected():
		print('connection established.')
		init_db()
	else:
		print('connection failed.')
		exit(-1)

	app.run('0.0.0.0', debug=True, port=15000)
