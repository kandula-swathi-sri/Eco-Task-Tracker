import os
import logging
from flask import Flask, request, jsonify, render_template
from random import choice
from datetime import date

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(_name_)
app.secret_key = os.environ.get("SESSION_SECRET", "eco-waste-management-secret-key")

# Recyclable waste types
recyclables = ['plastic', 'paper', 'metal', 'glass']
decompose_data = {
    "plastic": "Takes 500+ years to decompose",
    "paper": "Takes 2–6 weeks to decompose",
    "metal": "Takes 50–200 years to decompose",
    "glass": "Never decomposes naturally"
}

disposal_instructions = {
    "plastic": "Rinse and put in plastic recycle bin",
    "paper": "Tear and compost or recycle",
    "metal": "Send to metal recycling centers",
    "glass": "Wrap and place in glass bin"
}