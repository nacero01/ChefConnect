CREATE TABLE Role (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role_id int NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES Role(role_id)
);

CREATE TABLE Chef (
    chef_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id int NOT NULL,
    bio TEXT,
    specialty VARCHAR(255),
    rating DECIMAL(3, 2),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE ChefAvailability (
    availability_id INT AUTO_INCREMENT PRIMARY KEY,
    chef_id int NOT NULL,
    day_of_week VARCHAR(20) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    FOREIGN KEY (chef_id) REFERENCES Chef(chef_id)
);

CREATE TABLE MembershipPlan (
    plan_id INT AUTO_INCREMENT PRIMARY KEY,
    plan_name VARCHAR(255) NOT NULL UNIQUE,
    price DECIMAL(10, 2) NOT NULL,
    duration_months int NOT NULL
);

CREATE TABLE ChefMembership (
    membership_id INT AUTO_INCREMENT PRIMARY KEY,
    chef_id int NOT NULL,
    plan_id int NOT NULL,
    membership_type VARCHAR(255) NOT NULL,

    start_date DATE NOT NULL,
    end_date DATE NOT NULL,

    FOREIGN KEY (chef_id) REFERENCES Chef(chef_id)
    foreign key (plan_id) references MembershipPlan(plan_id)
);

CREATE TABLE Booking (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    chef_id int NOT NULL,
    user_id int NOT NULL,
    booking_date DATE NOT NULL,
    booking_time TIME NOT NULL,
    status VARCHAR(50) NOT NULL,
    customer_requests TEXT,
    FOREIGN KEY (chef_id) REFERENCES Chef(chef_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE Review (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    chef_id int NOT NULL,
    user_id int NOT NULL,
    rating DECIMAL(3, 2) NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chef_id) REFERENCES Chef(chef_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE Table Dish (
    dish_id INT AUTO_INCREMENT PRIMARY KEY,
    chef_id int NOT NULL,
    dish_name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (chef_id) REFERENCES Chef(chef_id)
);

CREATE TABLE BookingDish (
    booking_dish_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id int NOT NULL,
    dish_name VARCHAR(255) NOT NULL,
    quantity int NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES Booking(booking_id)
);

CREATE TABLE DishIngredient (
    dish_ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    dish_id int NOT NULL,
    ingredient_id int NOT NULL,
    quantity VARCHAR(255) NOT NULL,
    FOREIGN KEY (dish_id) REFERENCES Dish(dish_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredient(ingredient_id)
);

CREATE TABLE ingredient (
    ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    ingredient_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE ChefMembership (
    membership_id INT AUTO_INCREMENT PRIMARY KEY,
    chef_id int NOT NULL,
    plan_id int NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    FOREIGN KEY (chef_id) REFERENCES Chef(chef_id),
    FOREIGN KEY (plan_id) REFERENCES MembershipPlan(plan_id)
);

CREATE TABLE Payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    chef_id int NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(255) NOT NULL,
    FOREIGN KEY (chef_id) REFERENCES Chef(chef_id)
);

UPDATE Role SET role_name = 'Admin' WHERE role_id = 1;
UPDATE Role SET role_name = 'Chef' WHERE role_id = 2;
UPDATE Role SET role_name = 'User' WHERE role_id = 3;
SELECT * FROM Role;

SELECT * FROM User;

SELECT * FROM Chef;

SELECT chef_id, bio, specialty
FROM Chef;

TRUNCATE TABLE User;

INSERT INTO Chef (user_id)
SELECT user_id FROM User
WHERE username = 'chefnelson';

#Delete all data from User and Chef tables
SET FOREIGN_KEY_CHECKS = 0;
SET FOREIGN_KEY_CHECKS = 1;

SELECT * FROM ChefAvailability;
SELECT chef_id, bio, specialty
FROM Chef;

ALTER TABLE ChefAvailability
ADD CONSTRAINT unique_chef_schedule
UNIQUE (
    chef_id,
    day_of_week,
    start_time,
    end_time
);

SELECT * FROM Booking;

SELECT * FROM MembershipPlan;
SELECT * FROM ChefMembership;
SELECT chef_id, rating
FROM Chef;


