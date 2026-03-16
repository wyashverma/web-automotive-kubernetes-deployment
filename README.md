# laravel-automotive-kubernetes-deployment

Group No: D6 - Group 05
Project No: 	DO-16

**Project Description**

This project focuses on deploying a containerized Automotive PHP Laravel application on a Kubernetes cluster using Minikube. The main goal is to demonstrate modern DevOps practices by automating the deployment, scaling, and management of application containers. By using Kubernetes deployment and service manifests, the system ensures high availability, efficient resource management, and seamless application updates with minimal downtime.

**Project Overview**

The system demonstrates how a traditional web application can be transformed into a scalable cloud-native application using containerization and container orchestration technologies. The Laravel automotive application is first containerized using Docker and then deployed to a Kubernetes cluster running on Minikube. Kubernetes manages the application lifecycle including deployment, scaling, and rolling updates.

The deployment configuration includes Kubernetes Deployment and Service manifests that define how the application containers should run and communicate within the cluster. A key feature implemented in this project is Zero-Downtime Rolling Updates, which ensures that new application versions are deployed gradually without interrupting service availability.

**Objectives**

**Containerization**: Package the Laravel application into Docker containers for consistent execution across environments.
**Automation**: Automate deployment and management of containers using Kubernetes manifests.
**High Availability**: Ensure the application remains accessible during updates and failures.
**Scalability**: Enable the system to scale application instances based on demand.
**Reliability**: Implement rolling update strategies to avoid downtime during deployments.

**Technologies Used**

PHP Laravel
Docker
Kubernetes
Minikube
GitHub

**Project Architecture**

Laravel Application → Docker Container → Kubernetes Deployment → Kubernetes Service → Minikube Cluster

Steps to Run the Project
1. Start Minikube
minikube start

2. Build Docker Image
docker build -t laravel-automotive-app .

3. Apply Kubernetes Deployment
kubectl apply -f kubernetes/deployment.yaml

4. Apply Service
kubectl apply -f kubernetes/service.yaml

5. Access Application
minikube service laravel-service


Tech Stack
--------------------------------------------------------
1.Category	                   :   Tools / Technologies
2.Backend Framework	           :   PHP Laravel
3.Containerization             :   Docker
4.Container Orchestration	     :   Kubernetes
5.Local Kubernetes Cluster	   :   Minikube
6.Version Control	             :   Git
7.Repository Hosting	         :   GitHub
8.Infrastructure Management	   :   Kubernetes Deployment & Service Manifests

**Key Features**

**Containerized Laravel Application**: Docker used to package the Laravel automotive web application.
**Kubernetes Deployment**: Manages application pods and ensures desired state of containers.
**Service Configuration**: Kubernetes Service exposes the application to external users.
**Rolling Updates**: Enables zero-downtime updates while deploying new application versions.
**Scalability**: Kubernetes allows scaling the number of application pods as required.
**Local Kubernetes Environment**: Minikube used to simulate a production-like Kubernetes cluster locally.

**Group Members**
1. Mohit Kumar Gupta : EN22CS301607
2. Mohit Chauhan : EN22CS301605
3. Mouli Shukla : EN22CS301615
4. Nikhil Javery : EN22CS301647
5. Naman Pandey : EN22CS301630


**Conclusion**

The Laravel Automotive Application Deployment on Kubernetes project demonstrates how containerization and orchestration technologies can modernize web application deployment. By using Docker and Kubernetes, the project ensures scalability, reliability, and efficient resource management. The implementation of rolling updates guarantees continuous service availability during application updates, making the deployment process robust and production-ready.
