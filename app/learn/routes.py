# app/learn/routes.py
from flask import render_template, request
from app.learn import learn_bp
from app.db_connection import get_db

#개발자가 관심가져야 할 보안 취약점
@learn_bp.route('/learn')
def learn():
    return render_template('/learn/learn.html')

@learn_bp.route('/vuln', methods=['GET'])
def vuln():
    no = request.args.get('no', '')
    if no == '1':
        return render_template('/learn/sql_injection.html')
    elif no=='2':
        return render_template('/learn/xss.html')
    elif no=='3':
        return render_template('/learn/csrf.html')
    elif no=='4':
        return render_template('/learn/insecure_deserialization.html')
    elif no=='5':
        return render_template('/learn/security_misconfiguration.html')
    elif no=='6':
        return render_template('/learn/broken_authentication.html')
    elif no=='7':
        return render_template('/learn/sensitive_data_exposure.html')
    elif no=='8':
        return render_template('/learn/components_with_known_vulnerabilities.html')
    elif no=='9':
        return render_template('/learn/insufficient_logging.html')
    elif no=='10':
        return render_template('/learn/xxe.html')
    else:
        return render_template('/error.html')

#sql injection 공격 실습 페이지
@learn_bp.route('/practice/sql_injection', methods = ['GET','POST'])
def sql_injection():
    if request.method == 'POST':
        type = request.form['type']
        conn = get_db()
        cursor = conn.cursor()
        if int(type)<3:
            if int(type)==1:
                user_input = request.form.get('input','')
            elif int(type)==2:
                user_input = request.form.get('input2','')
                BLACKLIST=["#", "or"]
                for pattern in BLACKLIST:
                    if pattern in user_input:
                        return render_template('/learn/sql_injection_attack.html', type = int(type), message2="SQL Injection 감지")
            try:
                sql = f"SELECT * FROM sql{type} WHERE username ='{user_input}'"
                cursor.execute(sql)
                results = cursor.fetchall()
                message=f"쿼리 결과 : {results}"
            except Exception as e:
                message = f"쿼리 결과 : {str(e)}"
            finally:
                cursor.close()
                conn.close()
            if int(type)==1:
                return render_template('/learn/sql_injection_attack.html', type=1, message1=message)
            elif int(type)==2:
                return render_template('/learn/sql_injection_attack.html', type=2, message2=message)
        elif int(type)==3:
            user_input = request.form.get('input3', '')
            if user_input!='':
                try:
                    sql = "SELECT * FROM sql3 WHERE username = %s"
                    cursor.execute(sql, (user_input,))
                    results = cursor.fetchall()
                    message=f"쿼리 결과 : {results}"
                except Exception as e:
                    message = f"쿼리 결과 : {str(e)}"
                finally:
                    cursor.close()
                    conn.close()
                plusMsg = "Prepared Statement는 SQL 쿼리와 사용자의 입력값을 분리하여 SQL 인젝션 공격을 방어하는 기법입니다"
                return render_template('/learn/sql_injection_attack.html', type=3, message3=message,plusMsg= plusMsg)
            else :
                return render_template('/learn/sql_injection_attack.html', type=3)
    else:
        return render_template('/learn/sql_injection_attack.html', type=1)

#sql injection 실습 제출 페이지
@learn_bp.route('/practice/sql_injection/submit', methods = ['POST'])
def submit():
    type=request.form['type']
    user_flag = request.form['flag']
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT password from sql{type} WHERE username ='admin'")
    admin_password = cursor.fetchone()
    cursor.close()
    conn.close()
    if admin_password and user_flag == admin_password[0]:
        if int(type)==1:
            return render_template('/learn/sql_injection_attack.html', type=1, message1="성공")
        elif int(type)==2:
            return render_template('/learn/sql_injection_attack.html', type=2, message2="성공")
        else:
            return render_template('/learn/sql_injection_attack.html', type=3, message3="성공")
    else:
        if int(type)==1:
            return render_template('/learn/sql_injection_attack.html', type=1, messqge1="실패")
        elif int(type)==2:
            return render_template('/learn/sql_injection_attack.html', type=2, message2="실패")
        else:
            return render_template('/learn/sql_injection_attack.html', type=3, message3="실패")

#xss 실습 페이지
@learn_bp.route('/practice/xss', methods = ['GET', 'POST'])
def practice_xss():
    if request.method == 'POST':
        user_input = request.form.get('user_input','')
        return render_template('/learn/xss_practice.html',user_input=user_input)
    else:
        return render_template('/learn/xss_practice.html')

