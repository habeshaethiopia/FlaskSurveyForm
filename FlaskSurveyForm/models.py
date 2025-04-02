"""
Database models and functions for the training form application.

This module defines the database schema and functions for interacting with the database.
"""
import sqlite3
import json
import logging
from datetime import datetime

def get_db():
    """Get a database connection"""
    conn = sqlite3.connect('training_forms.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Create all database tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create training_forms table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            training_type TEXT NOT NULL,
            trainer_name TEXT,
            supplier_name TEXT,
            location_type TEXT NOT NULL,
            location_details TEXT,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            trainer_days REAL,
            trainees_data TEXT,
            submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_training_form(form_data):
    """Insert a new training form into the database."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO training_forms (
            training_type, trainer_name, supplier_name, location_type,
            location_details, start_date, end_date,
            trainer_days, trainees_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        form_data['training_type'],
        form_data.get('trainer_name'),
        form_data.get('supplier_name'),
        form_data['location_type'],
        form_data.get('location_details'),
        form_data['start_date'],
        form_data['end_date'],
        form_data.get('trainer_days'),
        form_data.get('trainees_data')
    ))
    
    form_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return form_id

def update_training_form(form_id, form_data):
    """Update an existing training form in the database."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE training_forms SET
            training_type = ?,
            trainer_name = ?,
            supplier_name = ?,
            location_type = ?,
            location_details = ?,
            start_date = ?,
            end_date = ?,
            trainer_days = ?,
            trainees_data = ?
        WHERE id = ?
    ''', (
        form_data['training_type'],
        form_data.get('trainer_name'),
        form_data.get('supplier_name'),
        form_data['location_type'],
        form_data.get('location_details'),
        form_data['start_date'],
        form_data['end_date'],
        form_data.get('trainer_days'),
        form_data.get('trainees_data'),
        form_id
    ))
    
    conn.commit()
    conn.close()
    return True

def get_training_form(form_id):
    """Get a training form by ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM training_forms WHERE id = ?
    ''', (form_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'training_type': row[1],
            'trainer_name': row[2],
            'supplier_name': row[3],
            'location_type': row[4],
            'location_details': row[5],
            'start_date': row[6],
            'end_date': row[7],
            'trainer_days': row[8],
            'trainees_data': row[9],
            'submission_date': row[10]
        }
    return None

def get_all_training_forms(search_term='', date_from=None, date_to=None, training_type=None, sort_by='submission_date', sort_order='DESC', page=1):
    """Get all training forms with optional filtering and pagination"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Build the query
    query = 'SELECT * FROM training_forms WHERE 1=1'
    params = []
    
    if search_term:
        query += ' AND (trainer_name LIKE ? OR supplier_name LIKE ? OR location_details LIKE ?)'
        search_param = f'%{search_term}%'
        params.extend([search_param, search_param, search_param])
    
    if date_from:
        query += ' AND start_date >= ?'
        params.append(date_from)
    
    if date_to:
        query += ' AND end_date <= ?'
        params.append(date_to)
    
    if training_type:
        query += ' AND training_type = ?'
        params.append(training_type)
    
    # Add sorting
    query += f' ORDER BY {sort_by} {sort_order}'
    
    # Add pagination
    query += ' LIMIT ? OFFSET ?'
    params.extend([10, (page - 1) * 10])
    
    # Get total count
    count_query = 'SELECT COUNT(*) FROM training_forms WHERE 1=1'
    count_params = params[:-2]  # Exclude LIMIT and OFFSET
    
    if search_term:
        count_query += ' AND (trainer_name LIKE ? OR supplier_name LIKE ? OR location_details LIKE ?)'
        search_param = f'%{search_term}%'
        count_params.extend([search_param, search_param, search_param])
    
    if date_from:
        count_query += ' AND start_date >= ?'
        count_params.append(date_from)
    
    if date_to:
        count_query += ' AND end_date <= ?'
        count_params.append(date_to)
    
    if training_type:
        count_query += ' AND training_type = ?'
        count_params.append(training_type)
    
    cursor.execute(count_query, count_params)
    total_count = cursor.fetchone()[0]
    
    # Get paginated results
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    forms = []
    for row in rows:
        forms.append({
            'id': row[0],
            'training_type': row[1],
            'trainer_name': row[2],
            'supplier_name': row[3],
            'location_type': row[4],
            'location_details': row[5],
            'start_date': row[6],
            'end_date': row[7],
            'trainer_days': row[8],
            'trainees_data': row[9],
            'submission_date': row[10]
        })
    
    conn.close()
    return forms, total_count