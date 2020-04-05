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