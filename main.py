from fastapi import FastAPI,Path,HTTPException,Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal,Optional
import json
app=FastAPI()

class Patient(BaseModel):
    id:Annotated[str,Field(...,description="ID of the patient",examples=["POO1","POO2"])]
    name:Annotated[str,Field(...,description="Name of the patient",examples=["Nitiesh","Devendra"])]
    city:Annotated[str,Field(...,description="City of patient ",examples=["Mumbai","Channai"])]
    age:Annotated[int,Field(...,description="Enter age of patient",examples=[12,15,16],gt=0,lt=120)]
    gender:Annotated[Literal["Male","Female","Other"],Field(...,description="enter gender of patient")]
    height:Annotated[float,Field(...,description="height of patient in mtrs",examples=[5.3,5.6,6],gt=0)]
    weight:Annotated[float,Field(...,description="weight of patient in kgs",examples=[56.7,60,67.8],gt=0)]
    @computed_field
    @property
    def bmi(self)->float:
        bmi=round(self.weight/(self.height**2),2)
        return bmi

    @computed_field
    @property
    def verdict(self)->str:
        if self.bmi<18.5:
            return "Underweight"
        elif self.bmi<30:
            return "Normal"
        else:
            return "oberse"

    
def load_data():
    with open("patients.json","r")as f:
        data=json.load(f)
    return data


def save_data(data):
    with open("patients.json","w")as f:
        json.dump(data,f)


class PatientUpdate(BaseModel):
    name:Annotated[Optional[str],Field(default=None,description="Name of the patient",examples=["Nitiesh","Devendra"])]
    city:Annotated[Optional[str],Field(default=None,description="City of patient ",examples=["Mumbai","Channai"])]
    age:Annotated[Optional[int],Field(default=None,description="Enter age of patient",examples=[12,15,16],gt=0,lt=120)]
    gender:Annotated[Optional[Literal["Male","Female","Other"]],Field(default=None,description="enter gender of patient")]
    height:Annotated[Optional[float],Field(default=None,description="height of patient in mtrs",examples=[5.3,5.6,6],gt=0)]
    weight:Annotated[Optional[float],Field(default=None,description="weight of patient in kgs",examples=[56.7,60,67.8],gt=0)]

@app.get("/")
def hello():
    return {"message":"Patient management api"}


@app.get("/about")
def about():
    return {"message":"A fully functional api to management your patient records"}

@app.get("/view")
def view():
    data=load_data()
    return data 

# s
# w
# 2
# x 
# @
@app.get("/patient/{patient_id}")
def  view_patient(patient_id:str=Path(...,description="ID of the patient in the DB",example="POO1")):
    data=load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail="Patient not found")


@app.get("/sort")
def sort_patient(sort_by:str=Query(...,description="sort on basis on height, weight , bmi"),order:str=Query("asc",description="sort on asc and desc order ")):
    valid_fields=["height","weight","bmi"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invaild feild select from {valid_fields}")
    if order not in ["asc","desc"]:
        raise HTTPException(status_code=400,detail="invalid sort order , choice asc and desc order")
    data=load_data()
    sort_order=True if order =="desc"else False
    sorted_data=sorted(data.values(),key=lambda t:t.get(sort_by,0), reverse= sort_order)
    return sorted_data


@app.post("/create")
def create_patient(patient:Patient):
    #load existing data
    data=load_data()
    #check patient allready exit or not
    if patient.id in data:
        raise HTTPException(status_code=400,detail="Patient allready exist")

    #new patient to DB
    data[patient.id] = patient.model_dump(exclude={"id"})

    #save into json file
    save_data(data)

    return JSONResponse(status_code=201,content={"message":"patient created successfully"})

@app.put("/edit/{patient_id}")
def update_patient(patient_id:str,patient_update:PatientUpdate):
    data=load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404,detail="Patient not found")
    existing_patient_info =data[patient_id]
    updated_patient_info=patient_update.model_dump(exclude_unset=True)
    for key,value in updated_patient_info.items():
        existing_patient_info[key]=value

    # existing_patient_info ->pydantic object ->updated bmi +verdict ->pydantic object->dict

    existing_patient_info["id"]=patient_id
    patient_pydantic_obj=Patient(**existing_patient_info)
    existing_patient_info=patient_pydantic_obj.model_dump(exclude={"id"})

    data[patient_id]=existing_patient_info
    save_data(data)
    return JSONResponse(status_code=200,content={"message":"patient data updated successfully"})


@app.delete("/delete/{patient_id}")
def delete_patient(patient_id:str):
    data=load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404,detail="Patient not found")
    del data[patient_id]
    save_data(data)
    return JSONResponse(status_code=200,content={"message":"Patient successfully deleted"})
