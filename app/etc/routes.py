# app/etc/routes.py
from flask import render_template, session, redirect, url_for
from app.etc import about_bp
from functools import wraps
from app.db_connection import get_db, close_db
from flask_jwt_extended import decode_token
import config

#로그인 상태 체크를 위한 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('community.login'))
        return f(*args, **kwargs)
    return decorated_function

@about_bp.route('/')
def index():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, title, created_at, comments FROM notice ORDER BY created_at DESC LIMIT 5")
    notice= cur.fetchall()
    close_db()
    return render_template('/etc/index.html', notice = notice)

@about_bp.route('/background')
def background():
    return render_template('/etc/background.html')

@about_bp.route('/mypage')
@login_required
def mypage():
    user = decode_token(session['user']).get('sub')
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE username=%s", (user,))
    userInfo = cur.fetchone()
    
    #작성한 질문글
    cur.execute("SELECT * FROM question WHERE author=%s", (user,))
    userQuestion = cur.fetchall()
    #작성한 홍보글
    cur.execute("SELECT * FROM promotion WHERE author=%s", (user,))
    userPromotion = cur.fetchall()
    #작성한 건의사항
    cur.execute("SELECT * FROM suggestion WHERE author=%s",(user,))
    userSuggest=cur.fetchall()

    #공지에 작성한 댓글
    cur.execute("SELECT * FROM noticeComment WHERE author=%s",(user,))
    userNoticeComment = cur.fetchall()
    #질문글에 작성한 댓글
    cur.execute("SELECT * FROM questionComment WHERE author=%s",(user,))
    userQuestionComment = cur.fetchall()
    #홍보글에 작성한 댓글
    cur.execute("SELECT * FROM promotionComment WHERE author=%s", (user,))
    userPromotionComment = cur.fetchall()

    #모든 공지 목록
    cur.execute("SELECT id, title FROM notice")
    noticeTitle = cur.fetchall()
    #모든 질문 목록
    cur.execute("SELECT id, title FROM question")
    questionTitle = cur.fetchall()
    #모든 홍보글 목록
    cur.execute("SELECT id, title FROM promotion")
    promotionTitle = cur.fetchall()
   
    close_db()

    return render_template('/etc/mypage.html', user=user, userInfo=userInfo, userQuestion = userQuestion, userPromotion=userPromotion, userSuggest=userSuggest, userNoticeComment=userNoticeComment, userPromotionComment=userPromotionComment, userQuestionComment=userQuestionComment, noticeTitle=noticeTitle, questionTitle=questionTitle, promotionTitle=promotionTitle)
