from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import anaesthetics, attachments, drugs, hospitals, occupations, \
        operations, operative_records, patients, post_operative_records, \
        practitioners, premedication_records, preoperative_records, \
        prescriptions, referals, techniques, theaters, vitals_records, wards
