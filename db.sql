-- Active: 1728563037850@@127.0.0.1@3306@DevGuardZone
CREATE DATABASE DevGuardZone DEFAULT CHARACTER SET = 'utf8mb4';

USE DevGuardZone;

CREATE TABLE sql1 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL
);

INSERT INTO
    sql1 (username, password)
VALUES ('admin', 'password123'),
    ('user1', 'mypassword');

CREATE TABLE sql2 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL
);

INSERT INTO
    sql2 (username, password)
VALUES ('admin', 'password123'),
    ('user1', 'mypassword');

CREATE TABLE sql3 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL
);

INSERT INTO
    sql3 (username, password)
VALUES ('admin', 'password123'),
    ('user1', 'mypassword');

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL
);

ALTER TABLE users ADD COLUMN introduce TEXT;

CREATE TABLE IF NOT EXISTS notice (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    comments INT DEFAULT 0,
    likes INT DEFAULT 0
);

CREATE TABLE noticeComment (
    id INT AUTO_INCREMENT PRIMARY KEY, -- 댓글의 고유 ID
    author VARCHAR(100) NOT NULL, -- 작성자 이름
    content TEXT NOT NULL, -- 댓글 내용
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 댓글 작성 시간
    likes INT DEFAULT 0, -- 좋아요 수
    post_id INT NOT NULL, -- 댓글이 달린 게시물의 ID
    FOREIGN KEY (post_id) REFERENCES notice (id) ON DELETE CASCADE -- 게시물과 관계 설정
);

CREATE TABLE suggestion (
    id INT AUTO_INCREMENT PRIMARY KEY, -- 건의사항 고유 ID
    category VARCHAR(255) NOT NULL, -- 건의사항 분류 (예: 질문, 피드백, 제안 등)
    title VARCHAR(255) NOT NULL, -- 건의사항 제목
    content TEXT NOT NULL, -- 건의사항 내용
    author VARCHAR(100) NOT NULL, -- 작성자 (사용자 이름)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 작성일 (기본적으로 현재 시간)
    admin_response TEXT, -- 관리자 답변
    response_at TIMESTAMP DEFAULT NULL -- 관리자 답변 시간 (답변이 없으면 NULL)
);

CREATE TABLE promotion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    author VARCHAR(50) NOT NULL,
    image_path VARCHAR(255), -- 이미지 경로 저장
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    comments INT DEFAULT 0,
    likes INT DEFAULT 0
);

CREATE TABLE promotionComment (
    id INT AUTO_INCREMENT PRIMARY KEY, -- 댓글의 고유 ID
    author VARCHAR(100) NOT NULL, -- 작성자 이름
    content TEXT NOT NULL, -- 댓글 내용
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 댓글 작성 시간
    likes INT DEFAULT 0, -- 좋아요 수
    post_id INT NOT NULL, -- 댓글이 달린 게시물의 ID
    FOREIGN KEY (post_id) REFERENCES promotion (id) ON DELETE CASCADE -- 게시물과 관계 설정
);

CREATE TABLE question (
    id INT AUTO_INCREMENT PRIMARY KEY,
    author VARCHAR(50) NOT NULL, -- 작성자
    title VARCHAR(255) NOT NULL, -- 질문 제목
    content TEXT NOT NULL, -- 질문 내용
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- 작성일 (기본값: 현재 시간)
    likes INT DEFAULT 0, -- 좋아요 수 (기본값: 0)
    comments INT DEFAULT 0, -- 댓글 수 (기본값: 0)
    is_resolved BOOLEAN DEFAULT 0 -- 해결 완료 여부 (기본값: 0, 미해결 상태)
);

CREATE TABLE questionComment (
    id INT AUTO_INCREMENT PRIMARY KEY, -- 댓글의 고유 ID
    author VARCHAR(100) NOT NULL, -- 작성자 이름
    content TEXT NOT NULL, -- 댓글 내용
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 댓글 작성 시간
    likes INT DEFAULT 0, -- 좋아요 수
    post_id INT NOT NULL, -- 댓글이 달린 게시물의 ID
    FOREIGN KEY (post_id) REFERENCES question (id) ON DELETE CASCADE -- 게시물과 관계 설정
);