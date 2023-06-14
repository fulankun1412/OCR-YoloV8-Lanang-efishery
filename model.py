from ultralytics import YOLO
import cv2
from collections import OrderedDict
import numpy as np
import yaml
from google.cloud import vision
from google.cloud.vision_v1 import types
import os
from io import BytesIO
import boto3
import pandas as pd
from PIL import Image

os.environ['CLEARML_CONFIG_FILE'] = "clearml.conf"

from clearml import Task, InputModel

with open('config.yaml','r') as f:
    configModel = yaml.safe_load(f)

task = Task.init(project_name=configModel["clearml-project-config"]["project-name"], task_name=configModel["clearml-project-config"]["task-name"],
                 task_type=configModel["clearml-project-config"]["task-type"], reuse_last_task_id=configModel["clearml-project-config"]["id"])

inputModel = InputModel(project=configModel["clearml-project-config"]["project-name"], name=configModel["model-config"]["YOLO-model"],
                        only_published=configModel["model-config"]["published"], tags=configModel["model-config"]["tags"])

task.connect(inputModel)
pathToModel = inputModel.get_local_copy()

model = YOLO(pathToModel)
imgDelimiter = cv2.imread(configModel["model-config"]["delimiter"])
gcv_api_key_path = configModel["model-config"]["vision-key"]
imgSize = configModel["model-config"]["image-size"]

def hconcat_resize(img_list,img_delimiter, interpolation 
                   = cv2.INTER_CUBIC):
    h_max = 0
    w_total = 10
      # take minimum width
    h_max = max(img.shape[0]
                for img in img_list)
    
    h_max2 = max(h_max, img_delimiter.shape[0])

    
    for img in img_list:
        w_total += img.shape[1] + 5
        w_total += img_delimiter.shape[1] + 5
    
    img_backgroud = np.zeros((h_max2, w_total,3), dtype=np.uint8) ## create base background image with max width and total height of all image in img_list
    img_backgroud[:,:] = (255,255,255) ## colour of the background

    current_x = 0
    for img in img_list:

        # add an image to the final array and increment the y coordinate
        img_backgroud[:img.shape[0],current_x:img.shape[1]+current_x,:] = img
        current_x = current_x + img.shape[1] + 5

        # add a delimiter image to each cropped image
        img_backgroud[:img_delimiter.shape[0],current_x:img_delimiter.shape[1]+current_x,:] = img_delimiter
        current_x = current_x + img_delimiter.shape[1] + 5

    return img_backgroud

def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#====================== GOOGLE VISION #======================
client = vision.ImageAnnotatorClient.from_service_account_file(gcv_api_key_path) # VISION API KEY PATH

def get_text_response_from_path(BytesImage):

    output = None
    try:
        image = types.Image(content=BytesImage)
    except ValueError:
        output = "Cannot Read Input File"
        return output

    text_response = client.text_detection(image=image, image_context={"language_hints": ["id"]})
    text = text_response.text_annotations

    return text
#====================== END OF GOOGLE VISION ======================

def map_blocks(blocks, block_type):
    return {
        block['Id']: block
        for block in blocks
        if block['BlockType'] == block_type
    }

def get_children_ids(block):
    for rels in block.get('Relationships', []):
        if rels['Type'] == 'CHILD':
            yield from rels['Ids']

def getAccess(alpha, charlie, tetha, zulu):
    charlie = charlie.replace(zulu, "")
    tetha = tetha.replace(alpha, "")
    alpha = alpha.replace(charlie, "")
    alpha = alpha.replace(tetha, "")
    zulu = zulu.replace(tetha, "")
    zulu = zulu.replace(charlie, "")

    return alpha, zulu

def extractValue(img):
    scalingH, scalingW = img.shape[0]/imgSize, img.shape[1]/imgSize
    data = cv2.resize(img, (imgSize, imgSize))

    results = model.predict(data, imgsz = imgSize,
                            conf = configModel["model-config"]["conf"], iou = configModel["model-config"]["iou"],
                            save = configModel["model-config"]["save-mode"], save_conf = configModel["model-config"]["save-mode"],
                            save_crop = configModel["model-config"]["save-mode"], save_txt = configModel["model-config"]["save-mode"],
                            device = configModel["model-config"]["device-mode"])
    
    classes = results[0].names

    imgDict = {}
    finalDict = {}
    dictDataEntity = {}
    for boxes in results[0].boxes:
        for box in boxes:
            labelNo = int(box.cls)

            x1 = int(box.xyxy[0][0]*scalingW)
            y1 = int(box.xyxy[0][1]*scalingH)
            x2 = int(box.xyxy[0][2]*scalingW)
            y2 = int(box.xyxy[0][3]*scalingH)

            tempCrop = img[y1:y2, x1:x2]

            imgDict.update({labelNo:tempCrop})

    orderedDict = OrderedDict(sorted(imgDict.items()))
    for key, value in orderedDict.items():
        for classKey, classValue in classes.items(): 
            if key == classKey:
                finalDict[classValue] = value

    ACCESS_KEY, SECRET_KEY = getAccess(alpha = configModel["model-config"]["ALPHA"], charlie = configModel["model-config"]["CHARLIE"],
                                       tetha = configModel["model-config"]["TETHA"], zulu = configModel["model-config"]["ZULU"])

    dfs = []
    for key in finalDict.keys():
        if key == "excelData":
            tableImage = finalDict["excelData"]
            tableImage = Image.fromarray(tableImage)
            buffered = BytesIO()
            tableImage.save(buffered, format='PNG')

            client = boto3.client("textract", aws_access_key_id = ACCESS_KEY,
                                aws_secret_access_key= SECRET_KEY, region_name = configModel["model-config"]["AWS-REGION"])
            response = client.analyze_document( Document={'Bytes': buffered.getvalue()}, FeatureTypes=['TABLES'])

            blocks = response['Blocks']
            tables = map_blocks(blocks, 'TABLE')
            cells = map_blocks(blocks, 'CELL')
            words = map_blocks(blocks, 'WORD')
            selections = map_blocks(blocks, 'SELECTION_ELEMENT')

            for table in tables.values():
                # Determine all the cells that belong to this table
                table_cells = [cells[cell_id] for cell_id in get_children_ids(table)]

                # Determine the table's number of rows and columns
                n_rows = max(cell['RowIndex'] for cell in table_cells)
                n_cols = max(cell['ColumnIndex'] for cell in table_cells)
                content = [[None for _ in range(n_cols)] for _ in range(n_rows)]

                # Fill in each cell
                for cell in table_cells:
                    cell_contents = [
                        words[child_id]['Text']
                        if child_id in words
                        else selections[child_id]['SelectionStatus']
                        for child_id in get_children_ids(cell)
                    ]
                    i = cell['RowIndex'] - 1
                    j = cell['ColumnIndex'] - 1
                    content[i][j] = ' '.join(cell_contents)

                # We assume that the first row corresponds to the column names
                df = pd.DataFrame(content[1:], columns=content[0])
                dfs.append(df)

    finalDict.pop("excelData")

    img_v_resize = hconcat_resize(finalDict.values(),imgDelimiter) #
    gray_imgResize = get_grayscale(img_v_resize) # call the grayscaling function
    success, encoded_image = cv2.imencode('.jpg', gray_imgResize) # save the image in memory
    BytesImage = encoded_image.tobytes()
    a = cv2.resize(img_v_resize, (960, 540))
    #cv2.imwrite("test.jpg", gray_imgResize)

    text_response = get_text_response_from_path(BytesImage)

    #========== POST PROCESSING ================#
    dataEntity = text_response[0].description.strip() # show only the description info from gvision

    a = [i.split("\n") for i in dataEntity.split('PEMISAH') if i]


    value = []
    value.clear()
    for i in a:
        c = [d for d in i if d]
        listToStr = ' '.join([str(elem) for elem in c])
        stripListToStr = listToStr.strip()
        value.append(stripListToStr)

    i = 0

    for entity in classes.values():
        dictDataEntity[entity] = value[i]
        i+=1
        if len(value) == i:
            break

    for label in classes.values():
            if label not in dictDataEntity.keys() and label != "excelData":
                dictDataEntity[label] = "-"
    
    return results[0].plot(), dictDataEntity, df