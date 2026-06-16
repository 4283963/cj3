-- 创建数据库
CREATE DATABASE IF NOT EXISTS animal_rescue DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE animal_rescue;

-- 动物档案表
CREATE TABLE IF NOT EXISTS animals (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '名字',
    species VARCHAR(50) NOT NULL COMMENT '物种：猫/狗/其他',
    gender VARCHAR(10) COMMENT '性别',
    age VARCHAR(50) COMMENT '年龄',
    sterilized BOOLEAN DEFAULT FALSE COMMENT '绝育状态',
    health_status VARCHAR(200) COMMENT '健康情况',
    found_location VARCHAR(200) COMMENT '发现地点',
    description TEXT COMMENT '描述',
    image_url VARCHAR(500) COMMENT '图片URL',
    status VARCHAR(50) DEFAULT '待领养' COMMENT '状态：待领养/申请中/已领养',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='动物档案表';

-- 领养申请表
CREATE TABLE IF NOT EXISTS adoption_applications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    animal_id INT NOT NULL COMMENT '动物ID',
    applicant_name VARCHAR(100) NOT NULL COMMENT '申请人姓名',
    applicant_phone VARCHAR(20) NOT NULL COMMENT '申请人电话',
    applicant_email VARCHAR(100) COMMENT '申请人邮箱',
    applicant_address VARCHAR(500) COMMENT '申请人住址',
    living_condition TEXT COMMENT '居住条件',
    experience TEXT COMMENT '养宠经验',
    reason TEXT COMMENT '领养原因',
    status VARCHAR(50) DEFAULT '待审核' COMMENT '申请状态：待审核/已通过/已拒绝',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (animal_id) REFERENCES animals(id) ON DELETE CASCADE,
    INDEX idx_animal_id (animal_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='领养申请表';

-- 插入测试数据
INSERT INTO animals (name, species, gender, age, sterilized, health_status, found_location, description, image_url, status) VALUES
('橘宝', '猫', '公', '约2岁', TRUE, '健康，已驱虫免疫', '小区3号楼楼下', '性格温顺，喜欢蹭人，会用猫砂盆。', '', '待领养'),
('黑豆', '狗', '公', '约1岁', FALSE, '健康，已打疫苗', '小区北门花园', '活泼好动，对人友好，会简单指令。', '', '待领养'),
('小白', '猫', '母', '约6个月', FALSE, '健康', '小区5号楼地下室', '胆小但很粘人，熟悉后会非常亲人。', '', '待领养'),
('花花', '猫', '母', '约3岁', TRUE, '健康，已绝育', '小区垃圾站附近', '性格独立，不喜欢被抱，但会安静地陪在你身边。', '', '待领养'),
('大黄', '狗', '公', '约5岁', TRUE, '健康，已绝育', '小区停车场', '性格沉稳，对小孩子很友善，适合有小孩的家庭。', '', '待领养');
