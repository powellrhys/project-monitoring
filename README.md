# project-monitoring

### Project Codebase

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Terraform](https://img.shields.io/badge/terraform-%235835CC.svg?style=for-the-badge&logo=terraform&logoColor=white)
![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![PowerShell](https://img.shields.io/badge/PowerShell-%235391FE.svg?style=for-the-badge&logo=powershell&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![Gherkin BDD](https://img.shields.io/badge/Gherkin%20BDD-darkgreen?style=for-the-badge&logo=cucumber&logoColor=white)

### Project Github Action Pipelines

![Collect Workflow Data](https://github.com/powellrhys/project-monitoring/actions/workflows/collect_workflow_data.yml/badge.svg)
![Build & Deploy](https://github.com/powellrhys/project-monitoring/actions/workflows/build-and-deploy.yml/badge.svg)

### Codebase Coverage

[![codecov](https://codecov.io/gh/powellrhys/project-monitoring/graph/badge.svg?token=k3QQIbikcT)](https://codecov.io/gh/powellrhys/project-monitoring)
![GitHub issues](https://img.shields.io/github/issues/powellrhys/project-monitoring.svg)

### Codebase structure

```
project-monitoring
├── .github
│   └── workflows
├── backend
│   ├── functions
├── frontend
│   ├── functions
│   └── pages
├── infra
├── shared
│   ├── functions
│   └── interfaces
└── tests
    ├── features
    ├── integration_tests
    └── unit_tests
```

## Overview

**project-monitoring** is a full-stack monitoring and analytics tool built to visualize and track **GitHub Actions workflow activity** across all your repositories. It collects detailed workflow run data directly from the **GitHub API**, analyzes execution trends, and helps ensure that automated workflows remain **active, healthy, and performant** over time.

- Collects workflow data (status, duration, frequency) from **all repositories** in your GitHub organization or account.  
- Monitors activity to detect **stale, failing, or inactive workflows**.  
- Provides **interactive dashboards** to explore workflow performance and reliability trends.  
- Automates data refresh with **GitHub Actions** on a scheduled cron job.  
- Stores data securely in **Azure Blob Storage** for persistence and scalability.  

## Backend
- **Python-based backend** that interfaces with the GitHub REST API to collect workflow metadata and run statistics.  
- Implements **incremental updates** to minimize API calls and improve efficiency.  
- **Scheduled GitHub Actions job** automatically updates the dataset daily or weekly.  
- Processed data is normalized and stored in **Azure Blob Storage** for easy access by the frontend.  

## Frontend
- Built with **Streamlit** to provide an intuitive, interactive visualization experience.  
- Displays **repository-level summaries**, **workflow run durations**, **success/failure rates**, and **activity timelines**.  
- Includes filters by repository, branch, or date range for detailed exploration.  
- Highlights inactive or failing workflows to help prioritize maintenance.  

## Infrastructure
- Infrastructure-as-Code managed with **Terraform** in the `infra/` directory.  
- **Azure**-based deployment for scalability and security.  
- Data persistence handled by Azure Blob Storage, with optional caching for faster dashboard loads.  
- Streamlit app hosted on **Azure App Service** for production availability.  

## Testing
- **Pytest** suite for backend data processing validation and API integrity checks.  
- **Mock GitHub API responses** used to ensure robust testing without rate-limit dependency.  
- Frontend and integration tests validate dashboard rendering and data accuracy.  

## Deployment

The Streamlit application is deployed across both **Streamlit Cloud** and **Azure App Service**, enabling easy access and redundancy:

- [Azure App Service Deployment](https://powellrhys-project-monitoring.azurewebsites.net)  
- [Streamlit Cloud Deployment](https://powellrhys-project-monitoring.streamlit.app/)  

Both deployments are secured using **OAuth0 authentication**, ensuring that workflow data remains private.  

Below are example renders of the dashboard showing workflow trends, activity summaries, and performance insights.  

## Frontend Application

### Home Page
![Screenshot of Home Page](docs/assets/home_page.png?raw=true "Home Page")

### Workflow Overview Page
![Screenshot of Workflow Overview Page](docs/assets/workflow_overview_page.png?raw=true "Workflow Overview Page")

### Workflow Analysis Page
![Screenshot of Workflow Analysis Page](docs/assets/workflow_analysis_page.png?raw=true "Workflow Analysis Page")
