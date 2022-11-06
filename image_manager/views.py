import datetime
import io
import os
import cv2
from email.mime.image import MIMEImage

from PIL import Image as im
import torch
from django.core.paginator import Paginator
from django.core.mail import BadHeaderError, EmailMultiAlternatives
from django.http import HttpResponse

from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.edit import UpdateView, DeleteView

from .models import SparePartModel, StockModel
from .forms import StockModelForm, SparePartModelForm
from django.template import loader


class lastImageView(View):
    def get(self, request):
        result_obj = StockModel.objects.filter().last()
        context = {
            "objects": result_obj,
        }
        return render(request, 'image_manager/index.html', context)


def yolo_img_analysis(img, name_raw):
    img_instance = StockModel(
        title=str(datetime.datetime.now),
        raw_img=img,
    )
    img_instance.save()

    uploaded_img_qs = StockModel.objects.filter().last()
    img_bytes = uploaded_img_qs.raw_img.read()
    img = im.open(io.BytesIO(img_bytes))
    path_hubconfig = "yolov5_code"
    path_weightfile = "weights/best(bs-8-local-new).pt"  # or any custom trained model

    model = torch.hub.load(path_hubconfig, 'custom',
                           path=path_weightfile, source='local',
                           force_reload=True)

    results = model(img, size=832)
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
        print('Есть компоненты которые заканчиваются')
        subject = "Printer stock parts are ending"
        html_message = loader.render_to_string(
            'image_manager/email_template.html',
            {
                'ending_components': ending_components,
                'objects': StockModel.objects.filter().last(),
                'name': name,
            }
        )
        try:
            msg = EmailMultiAlternatives(subject, html_message,
                                         '*youremail@email.com*',
                                         ['*email@email.com*'])
            print('email prepared')
            msg.mixed_subtype = 'related'
            msg.attach_alternative(html_message, "text/html")
            img_dir_raw = 'media/images'
            img_dir_res = 'media/yolo_out'

            file_path = os.path.join(img_dir_raw, name_raw)
            with open(file_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(name_raw))
            msg.attach(img)
            print('raw img attached')
            file_path = os.path.join(img_dir_res, name)
            with open(file_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(name))
            msg.attach(img)
            print('res img attached')
            msg.send()
            print('email sent')
        except BadHeaderError:
            return HttpResponse('Найден некорректный заголовок')


class autoAnalysis(View):
    def get(self, request):
        #Turn on the camera
        cap = cv2.VideoCapture(0)
        #Set resolution of the camera
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # "Warm up" the camera so the picture is not dark
        for i in range(30):
            cap.read()

        # Take a picture
        ret, frame = cap.read()
        name_raw = 'img_raw' + str(datetime.datetime.now().strftime("%d%m%Y%H%M%S")) + '.jpg'
        # Turn off the camera
        cap.release()
        # Rename and save the picture
        directory = "media/images/"
        os.chdir(directory)
        cv2.imwrite(name_raw, frame)
        os.chdir("../..")
        img = "images/" + name_raw

        yolo_img_analysis(img, name_raw)

        return lastImageView.as_view()(self.request)


def manualAnalysis(request):
    if request.method == 'POST':
        form = StockModelForm(request.POST, request.FILES)
        if form.is_valid():
            img = request.FILES.get('raw_img')
            name_raw = request.FILES['raw_img'].name
            yolo_img_analysis(img, name_raw)
            result_obj = StockModel.objects.filter().last()
            form = StockModelForm()
            context = {
                "form": form,
                "objects": result_obj,
            }
            return render(request, 'image_manager/manual_analysis.html', context)
        else:
            form = StockModelForm()
        context = {
            "form": form
        }
        return render(request, 'image_manager/manual_analysis.html', context)
    else:
        form = StockModelForm()
        context = {
            "form": form
        }
        return render(request, 'image_manager/manual_analysis.html', context)


def spare_parts_info(request):
    show_on_page = 5
    spare_parts = SparePartModel.objects.all()
    page_number = int(request.GET.get("page", 1))
    paginator = Paginator(spare_parts, show_on_page)
    notes_page = paginator.get_page(page_number)
    context = {
        'page': notes_page,
        'on_page': show_on_page
    }
    return render(request, "image_manager/spare_parts_info.html", context)


class EditPartsView(UpdateView):
    model = SparePartModel
    form_class = SparePartModelForm
    template_name = 'image_manager/minval.html'
    success_url = '/partsinfo'


class DeletePartsView(DeleteView):
    model = SparePartModel
    template_name = 'image_manager/spare_parts_del.html'
    success_url = '/partsinfo'

