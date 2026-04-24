CREATE DATABASE IF NOT EXISTS CarRental;
USE CarRental;

CREATE TABLE Car (
    Plate_ID VARCHAR(20) PRIMARY KEY,
    Car_Model VARCHAR(50) NOT NULL,
    Year INT,
    Car_Status VARCHAR(20) CHECK (Car_Status IN ('Active', 'Rented', 'Out_of_Service'))
);

CREATE TABLE Office (
    Office_ID INT PRIMARY KEY AUTO_INCREMENT,
    Office_Name VARCHAR(50),
    Location VARCHAR(100)
);

CREATE TABLE Customer (
    Customer_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE,
    Phone VARCHAR(20)
);

CREATE TABLE Reservation (
    Reservation_ID INT PRIMARY KEY AUTO_INCREMENT,
    Start_Date DATE,
    End_Date DATE,
    Plate_ID VARCHAR(20),
    Customer_ID INT,
    Office_ID INT,
    FOREIGN KEY (Plate_ID) REFERENCES Car(Plate_ID),
    FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID),
    FOREIGN KEY (Office_ID) REFERENCES Office(Office_ID)
);

CREATE TABLE Payment (
    Payment_ID INT PRIMARY KEY AUTO_INCREMENT,
    Amount DECIMAL(10,2),
    Payment_Date DATE,
    Reservation_ID INT,
    FOREIGN KEY (Reservation_ID) REFERENCES Reservation(Reservation_ID)
);

INSERT INTO Car VALUES
('ABC123', 'Toyota Corolla', 2022, 'Active'),
('XYZ789', 'Honda Civic', 2021, 'Rented'),
('LMN456', 'Kia Sportage', 2023, 'Active');

INSERT INTO Office (Office_Name, Location) VALUES
('Main Branch', 'Cairo'),
('Alex Branch', 'Alexandria');

INSERT INTO Customer (Name, Email, Phone) VALUES
('Ahmed Ali', 'ahmed@mail.com', '0100000000'),
('Sara Mohamed', 'sara@mail.com', '0111111111');

INSERT INTO Reservation (Start_Date, End_Date, Plate_ID, Customer_ID, Office_ID) VALUES
('2026-05-01', '2026-05-05', 'ABC123', 1, 1),
('2026-06-01', '2026-06-03', 'XYZ789', 2, 2);

INSERT INTO Payment (Amount, Payment_Date, Reservation_ID) VALUES
(500.00, '2026-05-01', 1),
(300.00, '2026-06-01', 2);

SELECT * FROM Car;
SELECT * FROM Customer;
SELECT * FROM Reservation;
SELECT * FROM Payment;