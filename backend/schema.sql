DROP TABLE IF EXISTS Role;
DROP TABLE IF EXISTS USER;
DROP TABLE IF EXISTS Chef;
DROP TABLE IF EXISTS ChefAvailability;
DROP TABLE IF EXISTS MembershipPlan;
DROP TABLE IF EXISTS ChefMembership;
DROP TABLE IF EXISTS Booking;
DROP TABLE IF EXISTS Review;
DROP TABLE IF EXISTS Dish;
DROP TABLE IF EXISTS BookingDish;
DROP TABLE IF EXISTS Ingredient;
DROP TABLE IF EXISTS DishIngredient;
DROP TABLE IF EXISTS Payment;
DROP TABLE IF EXISTS ClientPantry;
DROP TABLE IF EXISTS BookingIngredientRequest;
DROP TABLE IF EXISTS FavoriteChef;

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
    user_id int NOT NULL UNIQUE,
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
    unique (chef_id, day_of_week, start_time, end_time),
    check (day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    check (start_time < end_time),
    FOREIGN KEY (chef_id) REFERENCES Chef(chef_id) ON DELETE CASCADE
);

CREATE TABLE MembershipPlan (
    plan_id INT AUTO_INCREMENT PRIMARY KEY,
    plan_name VARCHAR(255) NOT NULL UNIQUE,
    price DECIMAL(10, 2) NOT NULL,
    duration_months int NOT NULL
);

CREATE TABLE ChefMembership (
    membership_id INT AUTO_INCREMENT PRIMARY KEY,
    chef_id INT NOT NULL,
    plan_id INT NOT NULL,
    membership_type VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,

    FOREIGN KEY (chef_id) REFERENCES Chef(chef_id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES MembershipPlan(plan_id),

    UNIQUE (chef_id, plan_id, start_date, end_date),
    CHECK (end_date >= start_date)
);

CREATE TABLE Booking (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    chef_id INT NOT NULL,
    user_id INT NOT NULL,
    booking_date DATE NOT NULL,
    booking_time TIME NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    customer_requests TEXT,

    FOREIGN KEY (chef_id) REFERENCES Chef(chef_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id),

    UNIQUE (chef_id, booking_date, booking_time),
    CHECK (status IN ('pending', 'accepted', 'declined', 'cancelled', 'completed'))
);

CREATE TABLE Review (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    chef_id int NOT NULL,
    user_id int NOT NULL,
    rating DECIMAL(3, 2) NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chef_id) REFERENCES Chef(chef_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    unique (chef_id, user_id),
    CHECK (rating >= 1 AND rating <= 5)
);

CREATE Table Dish (
    dish_id INT AUTO_INCREMENT PRIMARY KEY,
    chef_id int NOT NULL,
    dish_name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (chef_id) REFERENCES Chef(chef_id) ON DELETE CASCADE,
    unique (chef_id, dish_name),
    check (price >= 0)
);

CREATE TABLE BookingDish (
    booking_dish_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    dish_id INT NOT NULL,
    quantity INT NOT NULL,

    FOREIGN KEY (booking_id) REFERENCES Booking(booking_id),
    FOREIGN KEY (dish_id) REFERENCES Dish(dish_id),

    UNIQUE (booking_id, dish_id),
    CHECK (quantity > 0)
);

CREATE TABLE Ingredient (
    ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    ingredient_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE DishIngredient (
    dish_ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    dish_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    quantity VARCHAR(255) NOT NULL,

    FOREIGN KEY (dish_id) REFERENCES Dish(dish_id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredient(ingredient_id),

    UNIQUE (dish_id, ingredient_id)
);

CREATE TABLE Payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    chef_id int NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(255) NOT NULL,
    FOREIGN KEY (chef_id) REFERENCES Chef(chef_id)
);

CREATE TABLE ClientPantry (
    pantry_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    quantity VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    UNIQUE (user_id, item_name)
);

CREATE TABLE BookingIngredientRequest (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    ingredient_name VARCHAR(255) NOT NULL,
    quantity VARCHAR(100),
    notes TEXT,
    FOREIGN KEY (booking_id) REFERENCES Booking(booking_id),
    UNIQUE (booking_id, ingredient_name)
);

CREATE TABLE FavoriteChef (
    favorite_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    chef_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (chef_id) REFERENCES Chef(chef_id) ON DELETE CASCADE,

    UNIQUE(user_id, chef_id)
);


TRUNCATE TABLE User;
#Delete all data from User and Chef tables
SET FOREIGN_KEY_CHECKS = 0;
SET FOREIGN_KEY_CHECKS = 1;
