# CloudIA: Connecting Need and Help in Real Time

<div align="center">
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/googlecloud/googlecloud-original.svg" height="60" alt="Google Cloud" />
  <img width="20" />
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" height="60" alt="Python" />
  <img width="20" />
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/terraform/terraform-original.svg" height="60" alt="Terraform" />
</div>

## 📌 Project Description

CloudIA is a technological solution designed to address critical challenges in humanitarian aid management during emergency situations. The system leverages the power of cloud computing and artificial intelligence to efficiently connect people in need with volunteers willing to help — all in real time.

### Identified Challenges

- **Lack of coordination** between aid organizations and affected individuals  
- **Delays in response** to urgent needs  
- **Lack of visibility** of specific needs across different areas  
- **Inefficient distribution** of resources and volunteers  
- **No real-time updates** on the situation  

## 🎯 Objective

CloudIA’s primary goal is to create an automated connection system between people in need and volunteers, using AI and cloud services to optimize aid delivery and resource distribution during emergencies.

## 🛠️ Technologies Used

<table>
  <tr>
    <td><b>Cloud Infrastructure</b></td>
    <td>
      • Google Cloud Platform (GCP)<br>
      • Cloud Run (Serverless services)<br>
      • Cloud Functions<br>
      • Pub/Sub (Real-time messaging)<br>
      • Dataflow (Streaming data processing)<br>
      • BigQuery (Data analysis)
    </td>
  </tr>
  <tr>
    <td><b>Frontend</b></td>
    <td>• Telegram API (Main user interface)</td>
  </tr>
  <tr>
    <td><b>Development</b></td>
    <td>
      • Python (Business logic)<br>
      • Terraform (Infrastructure as Code)
    </td>
  </tr>
  <tr>
    <td><b>Artificial Intelligence</b></td>
    <td>
      • GPT-4o (Natural language processing)<br>
      • ReAct (Intelligent decision-making)
    </td>
  </tr>
</table>

## 🏗️ Solution Architecture

CloudIA is structured into several interconnected components:

### 1. User Interface
- Implemented via a Telegram bot  
- Provides easy access without the need for an additional app  

### 2. Data Processing
- **Data sources**: Collection of structured information  
- **Reading**: Processes incoming messages to extract key data  
- **Matching**: Smart matching system based on:  
  - Type of need  
  - Geographic location  
  - Specific requirements  

### 3. Data Transformation
The data flow follows three key stages:


- **Reading**: Capturing and analyzing messages  
- **Matching**: Algorithm that links needs with available resources  
- **Output**: Generation of notifications and real-time updates  

### 4. Storage
- Dedicated tables for successful and failed matches  
- Optimized system for real-time queries  
- Integration with BigQuery for historical analysis  

### 5. Infrastructure as Code
The entire deployment is managed through Terraform, enabling:
- Reproducible environments  
- Version control of infrastructure  
- Automated deployment  
- Modular components:  
  - Pub/Sub  
  - Help/Need generators  
  - AI Agent  
  - Telegram API  
  - Cloud Functions  

## 📊 Visualization and Results

The project includes dashboards for:

- Real-time monitoring of needs and assistance  
- Geographic analysis of affected individuals and volunteers  
- Statistics on the most common types of needs  
- Tracking the effectiveness of the matching system  
- Ongoing optimization based on historical data  

## 🔄 Workflow

1. Users submit needs or register as volunteers via Telegram  
2. The system processes the messages and extracts key information  
3. The matching engine pairs applicants with appropriate volunteers  
4. Both parties are notified when a match is found  
5. All information is stored for analysis and continuous improvement  

## 💡 Innovation and Scalability

CloudIA stands out for:

- **Real-time analytics** enabling immediate response  
- **Efficient data transformations** that speed up processes  
- **Data-driven optimization** for future operations  
- **Scalability** to any emergency context  

---
<img width="1077" alt="Screenshot 2025-03-31 at 10 23 12" src="https://github.com/user-attachments/assets/23a01d29-946b-46ea-97b6-84243ffa4a26" />


