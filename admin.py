from flask import Blueprint, render_template, request, redirect, flash, url_for, session, wrappers
from dbfunc import getConnection
from functools import wraps 

admin = Blueprint("admin",__name__)