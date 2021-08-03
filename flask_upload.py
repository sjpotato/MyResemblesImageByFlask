from flask import Flask, render_template, request

# #########################
# 1. 이미지 처리 관련 함수 정의
# #########################
# 1.1. 관련 모듈 로드
import os
import PIL
import exception
import face_recognition
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as img
import numpy as np

# C:\Users\xxxxx}\AppData\Local\Programs\Python\Python39\flaskEx\
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# #######################
# 1.2. 이미지 처리 함수 정의
# #######################
# 이미지에서 얼굴 구하기
def get_cropped_face(image_file):
    image = face_recognition.load_image_file(image_file)
    face_locations = face_recognition.face_locations(image)
    a, b, c, d = face_locations[0]
    cropped_face = image[a:c,d:b,:]
    
    return cropped_face

# 얼굴 임베딩 벡터를 구하는 함수
def get_face_embedding(face):
    return face_recognition.face_encodings(face)

# 얼굴간 거리를 구하는 함수 ( array 형태로 읽어 들여서, np_array로 변경 )
def get_distance(name1, name2):
    print(embedding_dict[name1], embedding_dict[name2])
    return np.linalg.norm(np.array(embedding_dict[name1])-np.array(embedding_dict[name2]), ord=2)

# name1과 name2의 거리를 비교하는 함수를 생성하되, name1은 미리 지정하고, name2는 호출시에 인자
def get_sort_key_func(name1):
    def get_distance_from_name1(name2):
        return get_distance(name1, name2)
    return get_distance_from_name1

# 폴더내의 이미지에 대해서 얼굴 임베딩 추출 및 dict 구성
def get_face_embedding_dict(dir_path):
    file_list = os.listdir(dir_path)
    embedding_dict = {}

    for file in file_list:
        print(file, end=', ')
        img_path = os.path.join(dir_path, file)

        # 1. 얼굴 이미지 로딩
        tmp_img = Image.open(img_path)
        img_array = np.asarray(tmp_img)

        # 2. embedding 값 추출
        embedding = get_face_embedding(img_array)
        if len(embedding) > 0:
            embedding_dict[os.path.splitext(file)[0]] = embedding[0]
        else:
            print('embedding is null:', file)  # 3. 추출 안된 경우는 dict에 포함 안함


    return embedding_dict


# ################################
# 2. 웹 처리 관련 
# ################################

app = Flask(__name__)

# 업로드 html
@app.route('/upload')
def render_file():
    return render_template('upload.html')

# 파일 업로드
@app.route('/fileUpload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        # 1. 업로드 이미지 저장
        f = request.files['file']
        f.save('static/images/upload/upload_img.jpg')

        # 2. 업로드 이미지 로딩 및 얼굴 추출
        # dir_path = 'C:\\Users\\chaeumcni\\AppData\\Local\\Programs\\Python\\Python39\\flaskEx\\static\\images\\face'
        upload_src_img = get_cropped_face('static/images/upload/upload_img.jpg')

        # 3. 업로드 embedding 값 추출
        upload_src_embedding = get_face_embedding(upload_src_img)
        print(upload_src_embedding)

        # 5. 업로드 이미지도 embedding_dict에 uploaded_img라는 이름으로 추가
        embedding_dict.update({'uploaded_img': upload_src_embedding})

        # 6. 닮은 이미지 5명 확인
        top = 5
        sort_key_func = get_sort_key_func('uploaded_img')
        sorted_faces = sorted(embedding_dict.items(), key=lambda x: sort_key_func(x[0]))

        image_list = dict()
        for i in range(top + 1):
            if i == 0:  # 첫번째로 나오는 이름은 자기 자신일 것이므로 제외합시다.
                continue
            if sorted_faces[i]:
                image_list.update({i: sorted_faces[i][0]})
                print('순위 {} : 이름({}), 거리({})'.format(i, sorted_faces[i][0], sort_key_func(sorted_faces[i][0])))


        return render_template('upload_result.html', image_list=image_list)


# 실행
if __name__ == '__main__':


    # 1. 얼굴 이미지 로딩
    # dir_path = 'C:\\Users\\xxxxx\\AppData\\Local\\Programs\\Python\\Python39\\flaskEx\\static\\images\\face'
    FACE_IMG_PATH = BASE_DIR + '\\static\\images\\face'

    # 2. 얼굴 이미지 로딩( 확장자 jpeg -> jpg로 모두 변경 )
    print('연예인 사진 읽기 시작!!')
    embedding_dict = get_face_embedding_dict(FACE_IMG_PATH)
    print('embedding 된 연예인 사진 수 :', len(embedding_dict))

    app.run(debug = True)



