-- MySQL MCP 演示数据库脚本
-- 生成时间: 2025-08-07 16:51:49

-- ==============================================
-- 1. 数据库和表结构创建
-- ==============================================

-- 创建演示数据库
CREATE DATABASE IF NOT EXISTS demo_aicraft DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用演示数据库
USE demo_aicraft;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    full_name VARCHAR(100) NOT NULL,
                    age INT,
                    city VARCHAR(50),
                    status ENUM('active', 'inactive', 'pending') DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_username (username),
                    INDEX idx_email (email),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建产品表
CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    price DECIMAL(10, 2) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    stock_quantity INT DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_category (category),
                    INDEX idx_price (price),
                    INDEX idx_active (is_active)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建订单表
CREATE TABLE IF NOT EXISTS orders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL DEFAULT 1,
                    unit_price DECIMAL(10, 2) NOT NULL,
                    total_amount DECIMAL(10, 2) NOT NULL,
                    order_status ENUM('pending', 'confirmed', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                    INDEX idx_user_id (user_id),
                    INDEX idx_product_id (product_id),
                    INDEX idx_status (order_status),
                    INDEX idx_date (order_date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================
-- 2. 测试数据插入
-- ==============================================

-- 插入用户数据
INSERT INTO users (username, email, full_name, age, city, status) VALUES
                ('alice_wang', 'alice.wang@example.com', '王爱丽', 28, '北京', 'active'),
                ('bob_zhang', 'bob.zhang@example.com', '张博', 32, '上海', 'active'),
                ('carol_li', 'carol.li@example.com', '李卡罗', 25, '深圳', 'active'),
                ('david_chen', 'david.chen@example.com', '陈大卫', 35, '广州', 'inactive'),
                ('eva_liu', 'eva.liu@example.com', '刘伊娃', 29, '杭州', 'active'),
                ('frank_wu', 'frank.wu@example.com', '吴法兰', 27, '成都', 'pending'),
                ('grace_huang', 'grace.huang@example.com', '黄格蕾丝', 31, '武汉', 'active'),
                ('henry_zhao', 'henry.zhao@example.com', '赵亨利', 26, '西安', 'active'),
                ('iris_tang', 'iris.tang@example.com', '唐艾瑞丝', 30, '南京', 'active'),
                ('jack_feng', 'jack.feng@example.com', '冯杰克', 33, '重庆', 'inactive');

-- 插入产品数据
INSERT INTO products (name, description, price, category, stock_quantity, is_active) VALUES
                ('MacBook Pro 14寸', '苹果笔记本电脑，M3芯片，16GB内存，512GB存储', 15999.00, '电脑', 50, TRUE),
                ('iPhone 15 Pro', '苹果智能手机，A17 Pro芯片，256GB存储', 8999.00, '手机', 100, TRUE),
                ('iPad Air', '苹果平板电脑，M2芯片，256GB Wi-Fi版', 4999.00, '平板', 75, TRUE),
                ('AirPods Pro 2', '苹果无线耳机，主动降噪', 1899.00, '音频', 200, TRUE),
                ('Magic Keyboard', '苹果无线键盘，中文版', 799.00, '配件', 150, TRUE),
                ('Magic Mouse', '苹果无线鼠标，白色', 629.00, '配件', 120, TRUE),
                ('Apple Watch Series 9', '苹果智能手表，45mm GPS版', 3199.00, '穿戴', 80, TRUE),
                ('Studio Display', '苹果27寸5K显示器', 11499.00, '显示器', 30, TRUE),
                ('Mac mini', '苹果桌面电脑，M2芯片，8GB+256GB', 4499.00, '电脑', 60, TRUE),
                ('HomePod mini', '苹果智能音箱，深空灰', 749.00, '音频', 90, FALSE);

-- 插入订单数据
INSERT INTO orders (user_id, product_id, quantity, unit_price, total_amount, order_status, order_date) VALUES
                (1, 1, 1, 15999.00, 15999.00, 'delivered', '2024-07-15 10:30:00'),
                (1, 4, 1, 1899.00, 1899.00, 'delivered', '2024-07-15 10:35:00'),
                (2, 2, 1, 8999.00, 8999.00, 'shipped', '2024-07-20 14:20:00'),
                (3, 3, 1, 4999.00, 4999.00, 'confirmed', '2024-07-25 16:45:00'),
                (3, 5, 1, 799.00, 799.00, 'confirmed', '2024-07-25 16:50:00'),
                (5, 7, 1, 3199.00, 3199.00, 'pending', '2024-08-01 09:15:00'),
                (7, 9, 1, 4499.00, 4499.00, 'delivered', '2024-08-03 11:30:00'),
                (8, 6, 2, 629.00, 1258.00, 'shipped', '2024-08-05 15:20:00'),
                (9, 8, 1, 11499.00, 11499.00, 'pending', '2024-08-06 13:45:00'),
                (1, 10, 1, 749.00, 749.00, 'cancelled', '2024-08-07 08:30:00');

-- ==============================================
-- 3. 演示查询
-- ==============================================

-- 查看所有用户
-- SELECT id, username, full_name, city, status, created_at FROM users ORDER BY created_at;

-- 查看活跃用户数量
-- SELECT status, COUNT(*) as user_count FROM users GROUP BY status;

-- 查看所有产品
-- SELECT id, name, price, category, stock_quantity, is_active FROM products ORDER BY category, price;

-- 查看不同类别产品数量
-- SELECT category, COUNT(*) as product_count, AVG(price) as avg_price FROM products WHERE is_active = TRUE GROUP BY category;

-- 查看所有订单
-- SELECT o.id, u.full_name, p.name, o.quantity, o.total_amount, o.order_status, o.order_date FROM orders o JOIN users u ON o.user_id = u.id JOIN products p ON o.product_id = p.id ORDER BY o.order_date DESC;

-- 查看订单统计
-- SELECT order_status, COUNT(*) as order_count, SUM(total_amount) as total_revenue FROM orders GROUP BY order_status;

-- 查看用户购买统计
-- SELECT u.full_name, COUNT(o.id) as order_count, SUM(o.total_amount) as total_spent FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id, u.full_name ORDER BY total_spent DESC;

-- 查看热门产品
-- SELECT p.name, COUNT(o.id) as order_count, SUM(o.quantity) as total_sold, SUM(o.total_amount) as total_revenue FROM products p LEFT JOIN orders o ON p.id = o.product_id WHERE o.order_status != 'cancelled' GROUP BY p.id, p.name ORDER BY total_sold DESC LIMIT 5;

