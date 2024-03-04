from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from api.config import API_KEY



app = FastAPI()

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

class AddressRequest(BaseModel):
    address_1: str
    address_2: str
    address_3: str



def get_distance_and_time(api_key, origin, destination):
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    parameters = {
        "origins": origin,
        "destinations": destination,
        "key": api_key,
    }
    response = requests.get(base_url, params=parameters)
    print("Response Status Code:", response.status_code)  # Log status code
    print("Response Body:", response.text)  # Log response body

    response_data = response.json()
    
    if response_data['status'] == 'OK':
        element = response_data['rows'][0]['elements'][0]
        if element['status'] == 'OK':
            return element['distance']['text'], element['duration']['text']
    else:
        print("Failed Request Data:", parameters, flush = True)  # Log failed request data
    raise HTTPException(status_code=400, detail="Error with the Distance Matrix API request")

def get_readable_address(api_key, location):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    parameters = {
        "address": location,
        "key": api_key,
    }
    response = requests.get(base_url, params=parameters)
    response_data = response.json()
    
    if response_data['status'] == 'OK':
        # Extract the formatted address
        formatted_address = response_data['results'][0]['formatted_address']
        return formatted_address
    else:
        raise HTTPException(status_code=400, detail="Error with the Geocoding API request")

@app.post("/distance/")



async def calculate_distances(request: AddressRequest):
    print(API_KEY)
    
    addresses = [request.address_1, request.address_2, request.address_3]
    readable_addresses = [get_readable_address(API_KEY, address) for address in addresses]
    distances = {}
    durations = {}

    for i, origin in enumerate(addresses):
        for j, destination in enumerate(addresses):
            if i != j:
                distance, duration = get_distance_and_time(API_KEY, origin, destination)
                origin_readable = readable_addresses[i]
                destination_readable = readable_addresses[j]
                distances[f"{origin_readable}-{destination_readable}"] = distance
                durations[f"{origin_readable}-{destination_readable}"] = duration

    return {
        "message": "Calculations complete",
        "addresses": readable_addresses,  # Including readable addresses in the response
        "distances": distances,
        "durations": durations,
    }

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI server for Distance Calculation!"}
