# Distributed Kafka-Spark Pipeline for High-Velocity Data Streams

![Architecture Diagram](architecture/Distributed-Kafka-Spark-Pipeline-for-High-Velocity-Data-Streams%20Diagram.drawio.png)

---

## Project Overview

This project demonstrates **real-time financial transaction processing and monitoring** using **Apache Kafka, Apache Spark, and ELK Stack**. It is designed to **simulate high-velocity financial transactions**, process them in **real-time**, and provide **monitoring & logging capabilities**.

> **Note:** This is a **personal project**, running on **limited system resources** and not deployed in a cloud environment. Despite these constraints, it **effectively showcases** a scalable, production-style architecture.

---

## Business Use Case & Problem Statement

### What does this system do?
- Generates **financial transactions** (credit card, PayPal, bank transfers).
- Sends transactions to **Kafka** at a high velocity.
- Processes them **in real-time** using **Spark Streaming** to:
  - **Aggregate transaction amounts per merchant**.
  - **Detect anomalies (potential fraud)**.
- Stores and **monitors** data using **Prometheus, Grafana, and ELK Stack**.

###  Why is this important?
- **Banks, fintech companies, and stock markets** handle **millions of transactions per second**.
- **Fraud detection in real-time** is critical to prevent financial losses.
- **Monitoring system health** ensures stability & prevents transaction failures.

---

## System Architecture & Components

| **Component**         | **Technology Used**               | **Purpose** |
|----------------------|---------------------------------|-------------|
| **Data Producer**    | Python & Java (Kafka Producer API) | Generates **high-speed financial transactions**. |
| **Message Broker**   | Apache Kafka (Docker) | Stores & distributes transactions across brokers. |
| **Stream Processing** | Apache Spark (Python) | Aggregates transactions & detects fraud. |
| **Monitoring**       | Prometheus & Grafana | Tracks Kafka, Spark, and system performance. |
| **Logging**          | ELK Stack (Elasticsearch, Logstash, Kibana) | Stores logs for debugging and insights. |

---

##  How Data Flows Through the System

### ** 1. Data Production (Kafka Producers)**

####  **Python Producer (`main.py`)**
- Generates **synthetic transactions** (approx 1.2M+ per hour).
- Uses **Kafka Producer API** to publish messages to **financial_transactions** topic.
- Runs in **parallel producer threads** (`producer_data_in_parallel(3)`).

#### ☕ **Java Producer (`TransactionProducer.java`)**
- Generates **synthetic transactions** (approx 150k **per second**)
- An alternative producer written in **Java** for **high throughput**.
- Uses **ExecutorService** for **concurrent transaction publishing**.

#### ✅ **Simulated Transaction Schema**
| **Column**          | **Data Type**  | **Size(bytes)** | **Description** |
|---------------------|---------------|---------|----------------|
| `transactionId`    | `STRING`       | 36      | Unique identifier for each transaction. |
| `userId`           | `STRING`       | 12      | Represents the user making the transaction. |
| `amount`           | `DOUBLE`       | 8       | Transaction amount (randomized). |
| `transactionTime`  | `LONG`         | 8       | UNIX timestamp of transaction. |
| `merchantId`       | `STRING`       | 12      | Merchant receiving payment. |
| `transactionType`  | `STRING`       | 8       | "purchase" or "refund". |
| `location`         | `STRING`       | 12      | Location of transaction. |
| `paymentMethod`    | `STRING`       | 15      | "credit_card", "paypal", "bank_transfer". |
| `isInternational`  | `BOOLEAN`      | 5       | Whether the transaction is international. |
| `currency`         | `STRING`       | 5       | Currency code (USD, EUR, GBP, etc.). |

- total 120 bytes
- if generating 1.2 billion records per hour using java producer total size will be approx 216 GB (1.2billion * 120 bytes)
---

### ** 2️. Message Brokering (Kafka Cluster)**
- **Kafka Brokers (3) & Controllers (3)**  
  - Ensures **fault tolerance** with **replication**.
  - **Partitions data** for parallel processing.

####  **Kafka Topics**
| **Topic Name**             | **Partitions** | **Replication Factor** | **Retention** |
|---------------------------|--------------|---------------------|-------------|
| `financial_transactions`  | 5            | 3                   | 7 days      |
| `transaction_aggregates`  | 3            | 3                   | 7 days      |
| `transaction_anomalies`   | 3            | 3                   | 7 days      |

---

### ** 3️. Stream Processing (Apache Spark)**
####  **Spark Processor (`spark_processor.py`)**
- Reads **transaction data from Kafka** in **real-time**.
- Parses **raw JSON messages** into **structured data**.
- Performs:
  1. **Aggregation** → Computes **total transaction volume per merchant**.
  2. **Anomaly Detection** → Flags **high-frequency transactions** as potential fraud.
- Writes **processed data back to Kafka**.

####  **Kafka Streaming Configuration**
| **Stream Process**            | **Input Topic**         | **Output Topic**          | **Checkpoint Directory**  |
|------------------------------|------------------------|--------------------------|--------------------------|
| Transaction Aggregation      | `financial_transactions` | `transaction_aggregates`  | `/mnt/spark-checkpoints/aggregates` |
| Anomaly Detection           | `financial_transactions` | `transaction_anomalies`   | `/mnt/spark-checkpoints/anomalies`  |

---

### ** 4️. Monitoring & Logging**
####  **Prometheus & Grafana (System Monitoring)**
- **Prometheus**
  - Collects **metrics** from Kafka & Spark.
  - Tracks:
    - **Kafka broker health & lag**.
    - **Number of transactions processed per second**.
    - **Spark job execution metrics**.
- **Grafana**
  - Displays **real-time dashboards** for monitoring.

####  **ELK Stack (Log Management)**
- **Elasticsearch**: Stores logs from Kafka & Spark.
- **Logstash**: Collects, filters, and processes logs.
- **Kibana**: Provides a **searchable log dashboard**.

####  **Logs Captured**
- **Kafka transaction logs**.
- **Spark processing logs**.
- **System performance logs**.

---

##  Project Constraints & Limitations
Since this is a **personal project**, certain **limitations exist**:
1. **Limited hardware resources** → Running multiple Kafka brokers & Spark nodes on a **single machine** restricts performance.
2. **No cloud deployment** → A production system would use **AWS, Azure, or GCP**.

---

##  Summary & Key Takeaways
 **Real-time transaction processing** with **Kafka & Spark**.  
 **High-speed message handling** with **Kafka brokers**.  
 **System monitoring** via **Prometheus & Grafana**.  
 **Log analysis** with **ELK Stack**.  

Despite hardware constraints, this project **successfully demonstrates** a **production-style architecture** for **high-performance financial transaction processing**. 

