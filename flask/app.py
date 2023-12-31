from flask import Flask, flash, request, Response, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import json
import os
import mysql.connector
import atexit

app = Flask(__name__, instance_relative_config=True)
UPLOAD_FOLDER = '/flask/static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET'])
def get_upload_form():
    try:
        conn = mysql.connector.connect(user='root', password='rootroot', host='slideshowdb', port='3306', database='pictureframe')
        cursor = conn.cursor()
        cursor.execute('select p.name,o.picture_order from pictures p inner join picture_order o on p.id=o.picture_id order by o.picture_order asc')
        pictures = cursor.fetchall()
        cursor.execute('select key_value duration from settings where key_name=\'duration\'');
        duration = cursor.fetchall()
        cursor.close()
        return render_template('index.html',pictures=pictures, duration=duration[0][0])
    except Exception as e:
        return json.dumps("Whoops", 500)
    finally:
        conn.close()

@app.route('/upload', methods=['POST'])
def upload():
    try:
        conn = mysql.connector.connect(user='root', password='rootroot', host='slideshowdb', port='3306', database='pictureframe')
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Save filename to the DB
        cursor = conn.cursor()
        cursor.execute(f'insert into pictures (name) values (\'{filename}\')')
        # cursor.lastrowid has the ID of the last added item
        pic_id = cursor.lastrowid
        print(f'Added picture ID {pic_id}')
        # How many pictures do we have?
        cursor.execute(f'select count(*) from pictures')
        pic_count = cursor.fetchall()[0][0]
        # Set this picture as the last item in the list
        cursor.execute(f'insert into picture_order (picture_id,picture_order) values ({pic_id},{pic_count})')
        cursor.execute(f'update settings set key_value=1 where key_name=\'changed\'')
        conn.commit()
        return get_pictures()
    except Exception as e:
        return json.dumps("Whoops", 500)
    finally:
        conn.close()

@app.route('/update', methods=['POST'])
def update():
    data = request.form['list']
    return redirect(url_for('hello'))

@app.route('/updateduration', methods=['POST'])
def update_duration():
    try:
        data = request.get_json()
        duration = data['duration']
        conn = mysql.connector.connect(user='root', password='rootroot', host='slideshowdb', port='3306', database='pictureframe')
        cursor = conn.cursor()
        cursor.execute(f'update settings set key_value={duration} where key_name=\'duration\'')
        cursor.execute(f'update settings set key_value=1 where key_name=\'changed\'')
        conn.commit()
        return Response('OK', 200)
    except Exception as e:
        return json.dumps("Whoops", 500)
    finally:
        conn.close()
           
@app.route('/reorder', methods=['POST'])
def reorder():
    try:
        data = request.get_json()
        conn = mysql.connector.connect(user='root', password='rootroot', host='slideshowdb', port='3306', database='pictureframe')
        cursor = conn.cursor()
        cursor.execute('truncate table picture_order')
        order = 1
        for picture_id in data:
            cursor.execute(f'insert into picture_order (picture_id,picture_order) values ({picture_id}, {order})')
            order = order + 1
        cursor.execute(f'update settings set key_value=1 where key_name=\'changed\'')
        conn.commit()
        return Response('OK', 200)
    except Exception as e:
        return json.dumps("Whoops", 500)
    finally:
        conn.close()

@app.route('/pictures', methods=['GET'])
def get_pictures():
    try:
        conn = mysql.connector.connect(user='root', password='rootroot', host='slideshowdb', port='3306', database='pictureframe')
        cursor = conn.cursor()
        cursor.execute('select p.id,p.name,o.picture_order from pictures p inner join picture_order o on p.id=o.picture_id order by o.picture_order asc')
        pictures = cursor.fetchall()
        cursor.close()
        bytes = json.dumps(pictures)
        return Response(bytes, mimetype='application/json')
    except Exception as e:
        return Response(e, 500)
    finally:
        conn.close()

@app.route('/clearchange', methods=['GET'])
def reset_change():
    try:
        conn = mysql.connector.connect(user='root', password='rootroot', host='slideshowdb', port='3306', database='pictureframe')
        cursor = conn.cursor()
        cursor.execute('update settings set key_value=0 where key_name=\'changed\'')
        conn.commit()
        return Response('OK', 200)
    except Exception as e:
        return Response(e, 500)
    finally:
        conn.close()

@app.route('/getchange', methods=['GET'])
def get_change():
    try:
        conn = mysql.connector.connect(user='root', password='rootroot', host='slideshowdb', port='3306', database='pictureframe')
        cursor = conn.cursor()
        cursor.execute('select key_value from settings where key_name=\'changed\'')
        changed = cursor.fetchall()
        bytes = json.dumps(changed[0])
        cursor.close()
        return Response(bytes, mimetype='application/json')
    except Exception as e:
        return Response(e, 500)
    finally:
        conn.close()

@app.route('/getduration', methods=['GET'])
def get_duration():
    try:
        conn = mysql.connector.connect(user='root', password='rootroot', host='slideshowdb', port='3306', database='pictureframe')
        cursor = conn.cursor()
        cursor.execute('select key_value from settings where key_name=\'duration\'')
        duration = cursor.fetchall()
        bytes = json.dumps(duration[0])
        cursor.close()
        return Response(bytes, mimetype='application/json')
    except Exception as e:
        return Response(e, 500)
    finally:
        conn.close()

@app.route('/slideshow', methods=['GET'])
def render_slideshow():
    try:
        conn = mysql.connector.connect(user='root', password='rootroot', host='slideshowdb', port='3306', database='pictureframe')
        cursor = conn.cursor()
        cursor.execute('select p.id,p.name,o.picture_order from pictures p inner join picture_order o on p.id=o.picture_id order by o.picture_order asc')
        pictures = cursor.fetchall()
        cursor.close()
        return render_template('slideshow.html', pictures=pictures)
    except Exception as e:
        return Response(e, 500)
    finally:
        conn.close()

@app.route('/delpicture', methods=['POST'])
def delete_image():
    try:
        conn = mysql.connector.connect(user='root', password='rootroot', host='slideshowdb', port='3306', database='pictureframe')
        data = request.get_json()
        cursor = conn.cursor()
        cursor.execute(f'delete from picture_order where picture_id={data["id"]};')
        cursor.execute(f'delete from pictures where id={data["id"]}')
        cursor.execute(f'update settings set key_value=1 where key_name=\'changed\'')
        conn.commit()
        cursor.close()
        return Response("OK", 200)
    except Exception as e:
        return Response(e, 500)
    finally:
        conn.close()

if __name__ == "__main__":
    app.run()
