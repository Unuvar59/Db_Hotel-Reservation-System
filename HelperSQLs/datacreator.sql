INSERT INTO customers (customer_id, name, phone, e_mail) VALUES
(1, 'Natalie White', '+1-358-341-9775x125', 'nparker@example.net'),
(2, 'Jonathan Wright', '(828)318-7372x1759', 'michaelfuller@example.com'),
(3, 'Joseph Sanders', '(484)814-2833', 'joanna58@example.com'),
(4, 'Brian Edwards', '+1-864-358-3675x98666', 'chambersvalerie@example.org'),
(5, 'Susan Horton', '(304)313-9752', 'carla84@example.com'),
(6, 'Justin Estes', '001-967-883-9512', 'morganmcbride@example.net'),
(7, 'Jamie Hill', '475-988-0927', 'jessica37@example.com'),
(8, 'Justin Rice', '986.341.6216', 'jennifer09@example.com'),
(9, 'Dr. Steven Michael', '001-957-431-2002', 'randall90@example.com'),
(10, 'Julie Henry', '001-781-846-4542', 'maria43@example.org'),
(11, 'Kathryn Weaver', '234.867.1104', 'ramirezandrea@example.net'),
(12, 'Thomas Lewis', '(925)360-2950x75314', 'kimberlylara@example.com'),
(13, 'Theresa Williams', '8445874511', 'aadams@example.com'),
(14, 'Kristie Snow', '001-936-758-1427x33141', 'nunezwilliam@example.org'),
(15, 'David Santana', '001-318-916-8332x256', 'wilsonrachel@example.com'),
(16, 'Jody Reese', '(545)980-5111', 'murrayjacqueline@example.org'),
(17, 'Alfred Barton', '318.933.6071', 'thernandez@example.com'),
(18, 'Steven Green', '001-342-427-7868x448', 'stephanieschmitt@example.org'),
(19, 'Shawn Cross', '530-410-2193', 'nneal@example.net'),
(20, 'John Avila', '2589136472', 'mwilliams@example.net');

INSERT INTO employees (employee_id, name, position, contact) VALUES
(1, 'Anna Kennedy', 'Chef', '941-764-7898x7927'),
(2, 'Maxwell Zamora', 'Housekeeper', '600.348.0685x853'),
(3, 'Ryan Holland', 'Manager', '+1-603-273-2638'),
(4, 'Frederick Johnson', 'Receptionist', '(491)976-9512x6334'),
(5, 'Shannon Sanchez', 'Chef', '444-349-4712x7370'),
(6, 'Ryan Goodman', 'Manager', '001-827-752-6041x11040'),
(7, 'Christopher Peterson', 'Receptionist', '790.829.2633x993');

INSERT INTO events (event_id, event_name, date, participation_fee) VALUES
(1, 'Product Event', '2025-08-15', 98.58),
(2, 'Through Event', '2024-05-22', 118.92),
(3, 'Spring Event', '2025-07-06', 193.22),
(4, 'Coach Event', '2025-10-06', 189.29),
(5, 'Coach Event', '2025-10-27', 37.81),
(6, 'Exactly Event', '2024-09-14', 175.86);

INSERT INTO rooms (room_id, type, pricing, capacity) VALUES
(1, 'Single', 102.36, 1),
(2, 'Suite', 103.68, 3),
(3, 'Suite', 232.45, 4),
(4, 'Suite', 271.54, 4),
(5, 'Double', 169.43, 1),
(6, 'Double', 183.18, 2),
(7, 'Double', 143.12, 3),
(8, 'Single', 64.68, 4),
(9, 'Double', 262.57, 2),
(10, 'Single', 240.64, 1),
(11, 'Double', 58.96, 4),
(12, 'Suite', 217.33, 1),
(13, 'Single', 204.19, 1),
(14, 'Suite', 137.28, 3),
(15, 'Suite', 172.15, 4),
(16, 'Suite', 242.37, 3),
(17, 'Suite', 107.33, 4),
(18, 'Double', 119.82, 2),
(19, 'Single', 140.88, 1),
(20, 'Suite', 171.97, 1);

INSERT INTO reservations (reservation_id, customer_id, room_id, check_in_date, check_out_date) VALUES
(1, 4, 12, '2023-12-29', '2025-05-27'),
(2, 5, 1, '2024-02-21', '2025-09-02'),
(3, 6, 4, '2024-09-29', '2025-04-25'),
(4, 5, 8, '2024-01-04', '2025-10-14'),
(5, 11, 12, '2024-05-29', '2025-12-11'),
(6, 5, 20, '2024-05-18', '2025-08-17'),
(7, 7, 4, '2024-03-03', '2025-12-01'),
(8, 10, 6, '2024-05-27', '2025-11-19'),
(9, 19, 6, '2024-10-01', '2025-04-12'),
(10, 20, 19, '2024-05-28', '2025-07-15'),
(11, 12, 2, '2024-11-26', '2025-03-17'),
(12, 7, 10, '2024-04-16', '2025-08-15'),
(13, 5, 11, '2024-02-03', '2025-07-22'),
(14, 4, 3, '2024-07-17', '2025-07-21'),
(15, 8, 6, '2024-05-23', '2025-12-04');

INSERT INTO payments (payment_id, reservation_id, amount, payment_date) VALUES
(1, 1, 600.06, '2024-04-12'),
(2, 2, 557.43, '2024-10-03'),
(3, 3, 571.70, '2024-12-16'),
(4, 4, 139.70, '2025-01-18'),
(5, 5, 86.42, '2025-05-15'),
(6, 6, 579.01, '2024-06-06'),
(7, 7, 876.48, '2024-07-13'),
(8, 8, 826.98, '2025-04-22'),
(9, 9, 744.44, '2025-02-23'),
(10, 10, 664.11, '2025-05-30'),
(11, 11, 659.70, '2025-02-08'),
(12, 12, 720.52, '2024-06-20'),
(13, 13, 431.23, '2024-02-20'),
(14, 14, 458.70, '2025-04-21'),
(15, 15, 594.61, '2024-11-18');
INSERT INTO roomservices (service_id, room_id, service_type, cost) VALUES
(1, 1, 'WiFi', 24.95),
(2, 19, 'WiFi', 26.91),
(3, 12, 'Cleaning', 16.11),
(4, 4, 'WiFi', 36.77),
(5, 13, 'Breakfast', 16.90),
(6, 17, 'Cleaning', 18.04),
(7, 10, 'Breakfast', 48.14),
(8, 9, 'Cleaning', 37.14),
(9, 14, 'Breakfast', 48.50),
(10, 4, 'Cleaning', 13.08);

INSERT INTO feedback (feedback_id, customer_id, feedback_details, feedback_date) VALUES
(1, 17, 'Choose arrive others best find six avoid skill thousand health.', '2024-09-08'),
(2, 18, 'Trial talk offer land she language hold food between person upon get.', '2024-12-21'),
(3, 15, 'Occur knowledge maybe cost gun clear let nearly save story fire public.', '2024-02-19'),
(4, 1, 'Medical individual able reduce while future drive father view accept.', '2024-11-21'),
(5, 7, 'Push gun employee let certain impact old reflect.', '2024-05-28');

