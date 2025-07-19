#!/usr/bin/env python3
"""
Script de ejemplo para probar el course-pipeline con diferentes tipos de cursos.
Este script simula diferentes escenarios de entrada para el pipeline.
"""

import json
import sys
import os

# Añadir el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import course_pipeline

def test_basic_course():
    """Prueba con un curso básico de programación"""
    course_data = {
        "id": 1001,
        "title": "Python Programming for Beginners",
        "description": "Learn the fundamentals of Python programming language from scratch",
        "instructor": "Prof. John Doe",
        "duration": "6 weeks",
        "level": "Beginner",
        "topics": ["Variables", "Loops", "Functions", "Data Structures"],
        "skills": ["Python", "Programming Logic", "Problem Solving"],
        "prerequisites": "No programming experience required",
        "learning_objectives": "Write basic Python programs, understand programming concepts, solve simple problems"
    }
    
    print("=== Testing Basic Course ===")
    test_event = {'body': json.dumps(course_data)}
    result = course_pipeline(test_event, None)
    print(f"Result: {result}\n")

def test_advanced_course():
    """Prueba con un curso avanzado de machine learning"""
    course_data = {
        "id": 1002,
        "title": "Advanced Deep Learning with TensorFlow",
        "description": "Master advanced deep learning techniques using TensorFlow 2.0",
        "instructor": "Dr. Sarah Johnson",
        "duration": "12 weeks",
        "level": "Advanced",
        "topics": ["Neural Networks", "CNN", "RNN", "Transformers", "GANs"],
        "skills": ["Python", "TensorFlow", "Deep Learning", "Mathematics", "Statistics"],
        "prerequisites": "Strong Python skills, linear algebra, calculus, basic ML knowledge",
        "learning_objectives": "Build complex neural networks, implement state-of-the-art architectures, deploy models in production"
    }
    
    print("=== Testing Advanced Course ===")
    test_event = {'body': json.dumps(course_data)}
    result = course_pipeline(test_event, None)
    print(f"Result: {result}\n")

def test_intermediate_course():
    """Prueba con un curso intermedio de desarrollo web"""
    course_data = {
        "id": 1003,
        "title": "Full-Stack Web Development with React and Node.js",
        "description": "Build complete web applications using modern JavaScript frameworks",
        "instructor": "Mike Chen",
        "duration": "10 weeks",
        "level": "Intermediate",
        "topics": ["React", "Node.js", "Express", "MongoDB", "REST APIs"],
        "skills": ["JavaScript", "React", "Node.js", "HTML/CSS", "Database Design"],
        "prerequisites": "Basic JavaScript knowledge and HTML/CSS fundamentals",
        "learning_objectives": "Create full-stack applications, implement REST APIs, deploy web applications"
    }
    
    print("=== Testing Intermediate Course ===")
    test_event = {'body': json.dumps(course_data)}
    result = course_pipeline(test_event, None)
    print(f"Result: {result}\n")

def test_data_science_course():
    """Prueba con un curso de data science"""
    course_data = {
        "id": 1004,
        "title": "Data Science and Analytics",
        "description": "Learn data analysis, visualization, and statistical modeling techniques",
        "instructor": "Dr. Emily Rodriguez",
        "duration": "8 weeks",
        "level": "Intermediate",
        "topics": ["Data Analysis", "Statistical Modeling", "Data Visualization", "Predictive Analytics"],
        "skills": ["Python", "Pandas", "NumPy", "Matplotlib", "Scikit-learn", "Statistics"],
        "prerequisites": "Basic Python programming and high school mathematics",
        "learning_objectives": "Analyze complex datasets, create visualizations, build predictive models, communicate insights"
    }
    
    print("=== Testing Data Science Course ===")
    test_event = {'body': json.dumps(course_data)}
    result = course_pipeline(test_event, None)
    print(f"Result: {result}\n")

def test_cybersecurity_course():
    """Prueba con un curso de ciberseguridad"""
    course_data = {
        "id": 1005,
        "title": "Cybersecurity Fundamentals",
        "description": "Introduction to cybersecurity principles, threats, and defense mechanisms",
        "instructor": "Alex Thompson",
        "duration": "7 weeks",
        "level": "Beginner",
        "topics": ["Network Security", "Cryptography", "Ethical Hacking", "Incident Response"],
        "skills": ["Network Protocols", "Security Tools", "Risk Assessment", "Security Policies"],
        "prerequisites": "Basic computer literacy and networking concepts",
        "learning_objectives": "Understand security threats, implement basic security measures, conduct security assessments"
    }
    
    print("=== Testing Cybersecurity Course ===")
    test_event = {'body': json.dumps(course_data)}
    result = course_pipeline(test_event, None)
    print(f"Result: {result}\n")

def main():
    """Ejecutar todas las pruebas"""
    print("Starting Course Pipeline Tests...\n")
    
    try:
        test_basic_course()
        test_intermediate_course()
        test_advanced_course()
        test_data_science_course()
        test_cybersecurity_course()
        
        print("All tests completed!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 