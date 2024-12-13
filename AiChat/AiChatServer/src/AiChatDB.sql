CREATE DATABASE AiChatDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户表，使用UUID作为主键
CREATE TABLE users (
    id CHAR(36) PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delete_flag BOOLEAN DEFAULT FALSE
);


-- 创建会话表
CREATE TABLE sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    session_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 创建聊天记录表
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    sender VARCHAR(50) NOT NULL,
    message_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

-- 创建用户统计信息表，添加delete_flag列
CREATE TABLE user_statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    total_messages INT DEFAULT 0,
    user_limit INT DEFAULT -9999,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delete_flag BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 创建触发器：在插入消息后更新用户统计信息
DELIMITER //

CREATE TRIGGER after_message_insert
AFTER INSERT ON messages
FOR EACH ROW
BEGIN
    DECLARE userId CHAR(36);
    DECLARE userLastActive TIMESTAMP;
    
    -- 获取当前会话的用户ID和最后活跃时间
    SET userId = (SELECT user_id FROM sessions WHERE id = NEW.session_id);
    SET userLastActive = (SELECT last_active FROM sessions WHERE id = NEW.session_id);

    -- 仅在sender为'user'时执行更新操作
    IF NEW.sender = 'user' THEN
        -- 更新用户统计信息
        UPDATE user_statistics 
        SET total_messages = total_messages + 1,
            last_active = userLastActive
        WHERE user_id = userId;
    END IF;
END //

DELIMITER ;


DELIMITER //

CREATE PROCEDURE delete_user_proc(IN input_user_id CHAR(36))
BEGIN
    -- 将user_statistics表中对应用户的delete_flag标志设置为TRUE
    UPDATE user_statistics SET delete_flag = TRUE WHERE user_id = input_user_id;
    
    -- 删除messages表中所有session_id在sessions表中user_id为输入参数input_user_id的消息记录
    DELETE FROM messages WHERE session_id IN (SELECT id FROM sessions WHERE user_id = input_user_id);
    
    -- 删除sessions表中所有user_id为输入参数input_user_id的会话记录
    DELETE FROM sessions WHERE user_id = input_user_id;
    
    -- 将users表中id为输入参数input_user_id的用户记录的delete_flag设置为TRUE
    UPDATE users SET delete_flag = TRUE WHERE id = input_user_id;
END //

DELIMITER ;



-- 创建新用户的存储过程
DELIMITER //

CREATE PROCEDURE create_user_proc(
    IN user_uuid CHAR(36),
    IN user_name VARCHAR(50),
    IN user_password VARCHAR(255),
    IN user_role ENUM('admin', 'user')
)
BEGIN
    -- 插入用户记录
    INSERT INTO users (id, username, password, role, created_at)
    VALUES (user_uuid, user_name, user_password, user_role, CURRENT_TIMESTAMP);

    -- 如果用户角色是'user'，则插入用户统计信息记录
    IF user_role = 'user' THEN
        INSERT INTO user_statistics (user_id, total_messages, user_limit, last_active, created_at, delete_flag)
        VALUES (user_uuid, 0, -9999, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, FALSE);
    END IF;
END //

DELIMITER ;

-- 插入管理员账号
CALL create_user_proc('0', 'admin', '21232f297a57a5a743894a0e4a801fc3', 'admin');

-- 插入五名基础用户
CALL create_user_proc('1', 'user1', '1a1dc91c907325c69271ddf0c944bc72', 'user');
CALL create_user_proc('2', 'user2', '1a1dc91c907325c69271ddf0c944bc72', 'user');
CALL create_user_proc('3', 'user3', '1a1dc91c907325c69271ddf0c944bc72', 'user');
CALL create_user_proc('4', 'user4', '1a1dc91c907325c69271ddf0c944bc72', 'user');
CALL create_user_proc('5', 'user5', '1a1dc91c907325c69271ddf0c944bc72', 'user');

-- 修改五个user的total_messages为不同值
UPDATE user_statistics SET total_messages = 10 WHERE user_id = '1';
UPDATE user_statistics SET total_messages = 20 WHERE user_id = '2';
UPDATE user_statistics SET total_messages = 30 WHERE user_id = '3';
UPDATE user_statistics SET total_messages = 40 WHERE user_id = '4';
UPDATE user_statistics SET total_messages = 50 WHERE user_id = '5';