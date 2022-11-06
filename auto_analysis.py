
import os,sys
sys.path.append('.\Projects\Red_button')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.file")
import django
django.setup()

import io
import os
import datetime

import torch
from PIL import Image as im
from email.mime.image import MIMEImage

import cv2
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from image_manager.models import SparePartModel, StockModel


def CronAnalysis():
    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # "Прогреваем" камеру, чтобы снимок не был тёмным
    for i in range(30):
        cap.read()
        # Делаем снимок
    ret, frame = cap.read()
    print('Picture was taken')
    name_raw = 'img_raw' + str(datetime.datetime.now()) + '.jpg'
        # Отключаем камеру
    cap.release()
    base_dir = "Документы/Диплом/Red_button"
    directory = "media/images/"
    directory = os.path.join(base_dir, directory)
    print('Start directory:', os.getcwd())
    os.chdir(directory)
    print('Directory was set up:', os.getcwd())
    cv2.imwrite(name_raw, frame)
    os.chdir("../..")
    print('Image saved. Directory was set up:', os.getcwd())
    img = "images/" + name_raw

    img_instance = StockModel(
        title=str(datetime.datetime.now),
        raw_img=img,
    )
    img_instance.save()
    print('Raw image saved to the model')
    uploaded_img_qs = StockModel.objects.filter().last()
    img_bytes = uploaded_img_qs.raw_img.read()
    img = im.open(io.BytesIO(img_bytes))

    path_hubconfig = "yolov5_code"
    path_weightfile = "weights/best(832_b16_ep800).pt"  # or any custom trained model

    model = torch.hub.load(path_hubconfig, 'custom',
                           path=path_weightfile, source='local',
                           force_reload=True)

    results = model(img, size=832)
    print('Results ready')
    img_objects = {}
    objects = results.pandas().xyxy[0].value_counts('name')
    objects = objects.to_dict(img_objects)

    # check if number is in the model
    for spare_part in objects.keys():
        if not SparePartModel.objects.filter(item_number=spare_part).exists():
            sp_instance = SparePartModel(
                item_number=spare_part,
            )
            sp_instance.save()
    print('Absent spare parts checked or added')
    results.render()
    results.save(save_dir="media/yolo_out/")
    name = 'img_result' + str(datetime.datetime.now().strftime("%d%m%Y%H%M%S")) + '.jpg'
    # saving results into model
    os.rename("media/yolo_out/image0.jpg", 'media/yolo_out/' + name)
    # update a record with result img
    StockModel.objects.filter(id=StockModel.objects.last().id).update(result_img="yolo_out/" + name)
    # add all founded objects to the model
    all_obj_list = list(SparePartModel.objects.values_list('item_number', flat=True))
    for spare_part in all_obj_list:
        if spare_part not in objects.keys():  # check if there are not all objects on the image
            obj_qty = 0
        else:
            obj_qty = objects[spare_part]
        sp_p = SparePartModel.objects.get(item_number=spare_part)
        img_instance.SpareParts.create(SparePart=sp_p, quantity=obj_qty)
    print('Stock and qty saved to the model')
    # check if current values are less then min values
    current_model_values = StockModel.objects.filter(id=StockModel.objects.last().id).values(
        'SpareParts__SparePart__item_number', 'SpareParts__quantity')
    min_model_values = SparePartModel.objects.all().values('item_number', 'min_value')
    current_values = {}
    min_values = {}
    # making a dictionaries
    for i in current_model_values:
        current_values[str(i['SpareParts__SparePart__item_number'])] = int(i['SpareParts__quantity'])
    for j in min_model_values:
        min_values[str(j['item_number'])] = int(j['min_value'])
    ending_components = {}  # creating a dict for adding ending components
    for number in current_values:
        if current_values[number] <= min_values[number]:
            ending_components[number] = current_values[number]
    # check if ending components exist
    if (len(ending_components) != 0):
        print('Ending parts existed')
        subject = "Printer stock parts are ending"
        html_message = loader.render_to_string(
            'image_manager/email_template.html',
            {
                'ending_components': ending_components,
                'objects': StockModel.objects.filter().last(),
                'name': name,
            }
        )
        msg = EmailMultiAlternatives(subject, html_message,
                                     'ivanter13@gmail.com',
                                     ['ivanter13@gmail.com', 'ivan.zyurin@claas.com'])
        msg.mixed_subtype = 'related'
        msg.attach_alternative(html_message, "text/html")
        img_dir_raw = 'media/images'
        img_dir_res = 'media/yolo_out'

        file_path = os.path.join(img_dir_raw, name_raw)
        with open(file_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(name_raw))
        msg.attach(img)

        file_path = os.path.join(img_dir_res, name)
        with open(file_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(name))
        msg.attach(img)
        msg.send()
        print('Email sent')

CronAnalysis