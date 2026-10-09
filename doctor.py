from fastapi import FastAPI , Path,HTTPException,Query
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal,Optional

app = FastAPI()

class Patient(BaseModel):

    id :Annotated[str,Field(...,description='Id of the patient',examples=['P001'])]
    name : Annotated[str,Field(...,description='Name of the patient')]
    city : Annotated[str,Field(...,description='Name of the city')]
    age:Annotated[str,Field(...,gt=0,lt=0,description='Name of the city')]
    gender:Annotated[str,Field(Literal['male','female','other'],description='Gender of the patient')]
    height:Annotated[str,Field(...,gt=0,description='Height of the patient in meters')]
    weight:Annotated[str,Field(...,gt=0,description='Weight of the patient in kgs')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:

        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'

class PatientUpdate(BaseModel):
    id :Annotated[Optional[str],Field(...,description='Id of the patient',examples=['P001'])]
    name : Annotated[Optional[str],Field(...,description='Name of the patient')]
    city : Annotated[Optional[str],Field(...,description='Name of the city')]
    age:Annotated[Optional[str],Field(...,gt=0,lt=0,description='Name of the city')]
    gender:Annotated[Optional[str],Field(Literal['male','female','other'],description='Gender of the patient')]
    height:Annotated[Optional[str],Field(...,gt=0,description='Height of the patient in meters')]
    weight:Annotated[Optional[str],Field(...,gt=0,description='Weight of the patient in kgs')]

        

def load_data():
    with open('patient.json','r') as f:
        data = json.load(f)

    return data

def save_data(data):
    with open('patient.json','w') as f:
        json.dump(data,f)

@app.get("/")
def hello():
    return {'message': 'Hello , What can I help you?'}

@app.get("/about")
def about():
    return {'message':'Here we can cure your health'}

@app.get("/view")
def view():
    data = load_data()

    return data

@app.get('/view/{patient_id}')
def view_patient(patient_id:str = Path(...,description="Write the patient id",examples="P001")):
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail="Patient id not found")

@app.get('/sort')
def sort_patient(sort_by:str = Query(...,description='Sort on the basis of height,weight or bmi'),order:str = Query('asc',description='sort in asc or desc order')):

    valid_field = ['height','bmi','weight']

    if sort_by not in valid_field:
        raise HTTPException(status_code=400, detail=f'Invalid field select from {valid_field}')

    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail='Invalid order select between asc and desc')

    data = load_data()

    sorted_order = True if order =='desc' else False

    sorted_data = sorted(data.values(),key = lambda x:x.get(sort_by,0),reverse=False)

    return sorted_data

@app.post('/create')
def create_patient(patient:Patient):

    data = load_data()

    if patient.id in data:
        raise HTTPException(status_code=400,detail='Patient is already in the data')

    data[patient.id] = patient.model_dump(exclude=['id'])

    save_data(data)

    return JSONResponse(status_code=201,content={'message':'patient created successfully'})

@app.put("/edit/{patient_id}")
def update_patient(patient_id : str, patient_update: PatientUpdate):

    data= load_data()

    if patient_id not in data: 
        raise HTTPException(status_code=404,detail='Patient not found!')

    existing_patient_info = data[patient_id]

    updated_patient_info=patient_update.model_dump(exclude_unset=True)

    for key,value in updated_patient_info.items(): 
        existing_patient_info[key] = value 

    # existing_patient_info -> pydantic obj -> updated bmi + verdict

    existing_patient_info['id'] =  patient_id
    patient_pydantic_object = Patient(**existing_patient_info)

    # -> pydantic object -> dict
    existing_patient_info = patient_pydantic_object.model_dump(exclude='id')    

    data[patient_id] = existing_patient_info

    save_data(data)

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id:str):

    data = load_data()

    if patient_id not in data: 
        raise HTTPException(status_code=404,detail="Patient is dead ")

    del data[patient_id]

    save_data(data)
    