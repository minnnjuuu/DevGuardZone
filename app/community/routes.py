# app/login/routes.py
from flask import render_template, request, redirect, url_for, Flask, session, jsonify
from app.community import community_bp
from app.db_connection import get_db, close_db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, decode_token
import config
from functools import wraps
from datetime import datetime
import os

#로그인 상태 체크를 위한 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('community.login'))
        return f(*args, **kwargs)
    return decorated_function

@community_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username','')
        password = request.form.get('password','')
        confirm_password = request.form.get('confirm-password','')
        if password==confirm_password:        
            # get_db()를 사용하여 데이터베이스 연결 가져오기
            db = get_db()
            if db is None:
                message='데이터베이스 연결에 실패했습니다.'
                return render_template('community/register.html', error_message=message)

            cur = db.cursor()
            try:
                cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                db.commit()
                message='회원가입이 성공적으로 완료되었습니다!'
                return render_template('community/register.html', success_message=message)
            except Exception as e:
                db.rollback()
                message='회원가입 중 오류가 발생했습니다.'
                return render_template ('community/register.html', error_message=message)
            finally:
                cur.close()
        else:
            message = '비밀번호가 일치하지 않습니다'
            return render_template('community/register.html', error_message=message)
    
    return render_template('community/register.html')


# 로그인 페이지
@community_bp.route('/login')
def login_page():
    return render_template('/community/login.html')  # 로그인 HTML 템플릿 렌더링

#로그인 처리
@community_bp.route('/loginProcess', methods=['POST', 'GET'])
def login():
    if request.method=='POST':
        username=request.form.get('username','')
        password=request.form.get('password', '')
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT password FROM users WHERE username=%s", (username,))
        result = cur.fetchone()
        cur.close()
        
        if result and result[0]==password:
            # 토큰 생성 후 세션에 저장하거나 리다이렉트 처리
            access_token=create_access_token(identity=username)
            session['user'] = access_token

            # 로그인 성공 시 홈 페이지로 리디렉션
            return redirect(url_for('etc.index'))
        else:
    # 로그인 실패 시 오류 메시지 반환
            message="잘못된 사용자 이름 또는 비밀번호입니다."
            return render_template('/community/login.html', message=message)
    else:
        return render_template('/community/login.html')
#보호된 페이지
@community_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user),200

@community_bp.route('/logout')
def logout():
    session.pop('user', None)
    return render_template('/etc/index.html')

@community_bp.route('/community')
def community():
    db=get_db()
    cursor=db.cursor()

    #최신공지 2개 조회
    cursor.execute("SELECT title, likes, comments, created_at, id FROM notice ORDER BY created_at DESC LIMIT 2")
    recent_notices=cursor.fetchall()

    #최신 질문글 2개 조회
    cursor.execute("SELECT id, title, likes, comments, created_at FROM question ORDER BY created_at DESC LIMIT 2")
    recent_question = cursor.fetchall()

    #최긴 홍보글 2개 조회
    cursor.execute("SELECT id, title, likes, comments, created_at FROM promotion ORDER BY created_at DESC LIMIT 2")
    recent_promotion = cursor.fetchall()

    #최신 건의사항 2개 조회
    cursor.execute("SELECT title, created_at, response_at, id FROM suggestion ORDER BY created_at DESC LIMIT 2")
    recent_suggest=cursor.fetchall()
    cursor.close()

    return render_template('/community/community.html', recent_notices=recent_notices, recent_question = recent_question, recent_promotion=recent_promotion, recent_suggest=recent_suggest)

#admin이 공지 작성
@community_bp.route('/community/noticeBoard/create', methods=['GET', 'POST'])
def noticeCreate():
    if request.method=='POST':
        if decode_token(session['user']).get('sub')=='admin':
            title=request.form['title']
            content=request.form['content']
            db = get_db()
            cur = db.cursor()
            cur.execute("INSERT INTO notice (title, content) VALUES (%s, %s)", (title,content))
            db.commit()
            cur.close()
            return render_template('/community/noticeCreate.html', message="공지사항 작성 완료")
        else:
            return "You are not admin"
    return render_template('/community/noticeCreate.html')

#공지사항 조회
@community_bp.route('/community/noticeBoard')
@login_required
def noticeBoard():
    db = get_db()
    cursor = db.cursor()

    #공지글 목록을 작성일 기준 내림차순으로 조회
    cursor.execute("SELECT title, created_at, likes, comments, id FROM notice ORDER BY created_at DESC")
    notice=cursor.fetchall()
    cursor.close()

    return render_template('/community/noticeBoard.html', notice=notice)

#공지사항 상세보기
@community_bp.route('/community/noticeBoard/<int:id>', methods = ['GET', 'POST'])
@login_required
def view_post(id):
    if request.method=='POST':
        return redirect(url_for('community.noticeBoard', id=id))
    else:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT title, content, created_at, likes, comments, id FROM notice WHERE id = %s", (id,))
        post = cur.fetchone()
        if post:
            cur.execute("SELECT author, content, created_at, id, likes FROM noticeComment where post_id=%s ORDER BY created_at ASC",(id,))
            comment = cur.fetchall()

            return render_template('/community/noticeView.html',id = id, post=post, comment=comment)
        return render_template('/community/noticeBoard.html')
    
#공지사항 댓글 작성
@community_bp.route('/community/noticeBoard/createComment', methods=['POST'])
@login_required
def createComment():
    post_id = request.form['post_id']
    content = request.form['content']
    author = decode_token(session['user']).get('sub')

    db = get_db()
    cur = db.cursor()
    #noticeComment db에 추가
    cur.execute("INSERT INTO noticeComment (author, content, post_id) VALUES (%s, %s, %s)", (author, content, post_id))
    db.commit()
    #notice db에 추가
    cur.execute("UPDATE notice SET comments = comments + 1 WHERE id = %s", (post_id,))
    db.commit()

    cur.close()
    return render_template('/community/noticeAuto.html',id=post_id)

#공지글 좋아요 1증가
@community_bp.route('/community/noticeBoard/likePost', methods=['POST'])
@login_required
def likePost():
    #클라이언트에서 받은 데이터
    data = request.get_json()
    id = data.get('id')

    #데이터베이스 연결
    db=get_db()
    cur=db.cursor()

    #좋아요 1증가
    cur.execute("UPDATE notice SET likes = likes + 1 WHERE id = %s", (id,))
    db.commit()

    # 좋아요 개수 반환
    cur.execute("SELECT likes FROM notice WHERE id = %s", (id,))
    new_like_count = cur.fetchone()[0]
    cur.close()

    return jsonify({'success': True, 'new_like_count': new_like_count})

#공지 게시물 댓글 좋아요 1증가
@community_bp.route('/community/noticeBoard/likePostComment', methods=['POST'])
@login_required
def likeComment():
    # 클라이언트에서 받은 데이터
    data = request.get_json()
    comment_id = data.get('comment_id')

    # 데이터베이스에 연결
    db = get_db()
    cur = db.cursor()

    # 댓글의 좋아요 수를 1 증가시키는 SQL 쿼리 실행
    cur.execute("UPDATE noticeComment SET likes = likes + 1 WHERE id = %s", (comment_id,))
    db.commit()

    # 새로운 좋아요 수 반환
    cur.execute("SELECT likes FROM noticeComment WHERE id = %s", (comment_id,))
    new_like_count = cur.fetchone()[0]

    cur.close()

    # 성공적으로 좋아요 수가 증가되었으면, 새로운 좋아요 수를 JSON으로 반환
    return jsonify({'success': True, 'new_like_count': new_like_count})

#건의사항 조회
@community_bp.route('/community/suggestBoard')
@login_required
def suggestBoard():
    db = get_db()
    cursor = db.cursor()

    #건의사항 목록을 작성일 기준 내림차순으로 조회
    cursor.execute("SELECT category, title, author, created_at, response_at, id FROM suggestion ORDER BY created_at DESC")
    suggestion=cursor.fetchall()
    cursor.close()

    return render_template('/community/suggestBoard.html', suggestion=suggestion)

#건의사항 작성
@community_bp.route('/community/suggestBoard/createPost', methods=['POST', 'GET'])
@login_required
def suggestCreate():
    if request.method == 'POST':
        category=request.form['category']
        title=request.form['title']
        content=request.form['content']
        user = decode_token(session['user']).get('sub')
        
        db=get_db()
        cur=db.cursor()
        cur.execute("INSERT INTO suggestion (category, title, content, author) VALUES (%s, %s, %s, %s)", (category, title, content, user))
        db.commit()
        cur.close()        
        return render_template('/community/suggestBoard.html')
    return render_template('/community/suggestCreate.html')

#건의사항 상세보기
@community_bp.route('/community/suggestBoard/<int:id>', methods=['POST', 'GET'])
@login_required
def view_suggest(id):
    if request.method=='POST':
        return redirect(url_for('community.suggestBoard', id=id))
    else:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id, category, title, content, author, created_at, admin_response, response_at FROM suggestion WHERE id=%s", (id,))
        suggest = cur.fetchall()
        if suggest:
            formatted_data = list(suggest[0])
            return render_template('/community/suggestView.html', suggest=formatted_data, user=decode_token(session['user']).get('sub'))
        return render_template('/etc/error.html')

#건의사항 답변 작성
@community_bp.route('/community/suggestBoard/createComment', methods=['POST'])
@login_required
def suggestCreateComment():
    post_id = request.form['post_id']
    content = request.form['content']

    db=get_db()
    cur=db.cursor()
    #suggestion db에 관리자 답변 추가
    cur.execute("UPDATE suggestion SET admin_response=%s, response_at=%s WHERE id=%s",(content, datetime.now(), post_id))
    db.commit()
    cur.close()
    return render_template('community/suggestAuto.html', id=post_id)

#홍보 게시판
@community_bp.route('/community/promotionBoard')
@login_required
def promotionBoard():
    db = get_db()
    cursor = db.cursor()

    #홍보글 조회
    cursor.execute("SELECT title, created_at, likes, comments, id FROM promotion ORDER BY created_at DESC")
    promotion = cursor.fetchall()
    cursor.close()

    return render_template('/community/promotionBoard.html', promotion=promotion)

#홍보 게시글 작성
@community_bp.route('/community/promotionBoard/createPost', methods=['POST', 'GET'])
@login_required
def promotionCreate():
    if request.method =='POST':
        title = request.form['title']
        content = request.form['content']
        user = decode_token(session['user']).get('sub')
        
        imageFile=request.files['image']
        imagePath=None
        if imageFile:
            imagePath=os.path.join('app\\static\\uploads', imageFile.filename)
            imageFile.save(imagePath)   #서버에 이미지 저장
        
        #DB에 게시물 정보 저장
        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO promotion (title, content, author, image_path, created_at) VALUES (%s, %s, %s, %s, %s)", (title, content, user, imagePath, datetime.now()))
        db.commit()
        cur.close()

        return redirect(url_for('community.promotionBoard'))
    return render_template('/community/promotionCreate.html')

#홍보 게시물 상세보기
@community_bp.route('/community/promotionBoard/<int:id>', methods=['POST', 'GET'])
@login_required
def viewPromotion(id):
    if request.method=='POST':
        return redirect(url_for('community.promotionBoard', id=id))
    else:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id, title, content, author, image_path, created_at, comments, likes FROM promotion WHERE id = %s", (id,))
        promotion=cur.fetchone()
        if promotion:
            cur.execute("SELECT id, author, content, created_at, likes FROM promotionComment WHERE post_id=%s ORDER BY created_at ASC",(id,))
            comment = cur.fetchall()
            return render_template('/community/promotionView.html', promotion=promotion, comment=comment)
        return render_template('/community/promotionBoard.html')
    
#홍보글 좋아요 1증가
@community_bp.route('/community/promotionBoard/likePost', methods=['POST'])
@login_required
def promotionLikePost():
    #클라이언트에서 받은 데이터
    data = request.get_json()
    id = data.get('id')

    #데이터베이스 연결
    db=get_db()
    cur=db.cursor()

    #좋아요 1증가
    cur.execute("UPDATE promotion SET likes = likes + 1 WHERE id = %s", (id,))
    db.commit()

    # 좋아요 개수 반환
    cur.execute("SELECT likes FROM promotion WHERE id = %s", (id,))
    new_like_count = cur.fetchone()[0]
    cur.close()

    return jsonify({'success': True, 'new_like_count': new_like_count})

#홍보글 댓글 좋아요 1증가
@community_bp.route('/community/promotionBoard/likePostComment', methods=['POST'])
@login_required
def promotionLikeComment():
    # 클라이언트에서 받은 데이터
    data = request.get_json()
    comment_id = data.get('comment_id')

    # 데이터베이스에 연결
    db = get_db()
    cur = db.cursor()

    # 댓글의 좋아요 수를 1 증가시키는 SQL 쿼리 실행
    cur.execute("UPDATE promotionComment SET likes = likes + 1 WHERE id = %s", (comment_id,))
    db.commit()

    # 새로운 좋아요 수 반환
    cur.execute("SELECT likes FROM promotionComment WHERE id = %s", (comment_id,))
    new_like_count = cur.fetchone()[0]
    cur.close()

    # 성공적으로 좋아요 수가 증가되었으면, 새로운 좋아요 수를 JSON으로 반환
    return jsonify({'success': True, 'new_like_count': new_like_count})

#홍보 게시물 댓글 좋아요 1증가
@community_bp.route('/community/promotionBoard/createComment', methods=['POST'])
@login_required
def createPromotionComment():
    post_id = request.form['post_id']
    content = request.form['content']
    author = decode_token(session['user']).get('sub')

    db = get_db()
    cur = db.cursor()
    #promotionComment db에 추가
    cur.execute("INSERT INTO promotionComment (author, content, post_id) VALUES (%s, %s, %s)", (author, content, post_id))
    db.commit()
    #promotion db에 댓글 수 업데이트 
    cur.execute("UPDATE promotion SET comments = comments + 1 WHERE id = %s", (post_id,))
    db.commit()

    cur.close()
    return render_template('/community/promotionAuto.html', id=post_id)

@community_bp.route('/community/questionBoard')
@login_required
def questionBoard():
    db = get_db()
    cursor = db.cursor()

    #질문글 조회
    cursor.execute("SELECT id, title, created_at, likes, comments, is_resolved FROM question ORDER BY created_at DESC")
    question = cursor.fetchall()
    cursor.close()

    return render_template('/community/questionBoard.html', question=question)

@community_bp.route('/community/questionBoard/createQuestion', methods=['POST', 'GET'])
@login_required
def questionCreate():
    if request.method=='POST':
        title = request.form['title']
        content = request.form['content']
        user = decode_token(session['user']).get('sub')

        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO question (author, title, content) VALUES(%s, %s, %s)", (user, title, content))
        db.commit()
        cur.close()
        return redirect(url_for('community.questionBoard'))
    return render_template('/community/questionCreate.html')

#질문글 상세보기
@community_bp.route('/community/questionBoard/<int:id>', methods=['POST', 'GET'])
@login_required
def view_question(id):
    if request.method=='POST':
        return redirect(url_for('community.questionBoard'), id = id)
    else:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id, author, title, content, created_at, likes, comments, is_resolved FROM question WHERE id = %s", (id,))
        question = cur.fetchone()
        user = decode_token(session['user']).get('sub')
        if question:
            cur.execute("SELECT id, author, content, created_at, likes FROM questionComment WHERE post_id=%s ORDER BY created_at ASC",(id,))
            comment = cur.fetchall()
            return render_template('/community/questionView.html', id=id, question=question, comment = comment, user = user)
        return render_template('/community/questionBoard.html')

#질문글 댓글 작성
@community_bp.route('/community/questionBoard/createComment', methods = ['POST'])
@login_required
def createQuestionComment():
    post_id = request.form['post_id']
    content = request.form['content']
    author = decode_token(session['user']).get('sub')

    db = get_db()
    cur = db.cursor()
    #questionComment db에 추가
    cur.execute("INSERT INTO questionComment (author, content, post_id) VALUES (%s, %s, %s)", (author, content, post_id))
    db.commit()
    #question db에 추가
    cur.execute("UPDATE question SET comments = comments + 1 WHERE id = %s", (post_id,))
    db.commit()

    cur.close()
    return render_template('/community/questionAuto.html', id = post_id)

#질문글 좋아요 1증가
@community_bp.route('/community/questionBoard/likeQuestion', methods=['POST'])
@login_required
def likeQuestion():
    data = request.get_json()
    id = data.get('id')

    db = get_db()
    cur = db.cursor()
    
    #좋아요 1증가
    cur.execute("UPDATE question SET likes = likes + 1 WHERE id = %s", (id,))
    db.commit()

    #좋아요 개수 반환
    cur.execute("SELECT likes FROM question WHERE id = %s", (id,))
    new_like_count = cur.fetchone()[0]
    cur.close()

    return jsonify({'success': True, 'new_like_count': new_like_count})

#질문글 댓글 좋아요 1증가
@community_bp.route('/community/questionBoard/likeQuestionComment', methods=['POST'])
@login_required
def likeQuestionComment():
    # 클라이언트에서 받은 데이터
    data = request.get_json()
    comment_id = data.get('comment_id')

    # 데이터베이스에 연결
    db = get_db()
    cur = db.cursor()

    # 댓글의 좋아요 수를 1 증가시키는 SQL 쿼리 실행
    cur.execute("UPDATE questionComment SET likes = likes + 1 WHERE id = %s", (comment_id,))
    db.commit()

    # 새로운 좋아요 수 반환
    cur.execute("SELECT likes FROM questionComment WHERE id = %s", (comment_id,))
    new_like_count = cur.fetchone()[0]

    cur.close()

    # 성공적으로 좋아요 수가 증가되었으면, 새로운 좋아요 수를 JSON으로 반환
    return jsonify({'success': True, 'new_like_count': new_like_count})

#질문 해결로 바꾸기
@community_bp.route('/community/questionBoard/solved', methods=['POST'])
@login_required
def changeSolved():
    id = request.form['post_id']
    
    db = get_db()
    cur = db.cursor()

    cur.execute("UPDATE question SET is_resolved = 1 WHERE id = %s", (id,))
    db.commit()

    cur.close()

    return redirect(url_for('community.view_question', id=id))